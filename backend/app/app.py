"""
*Backend Architecture Overview:
This application is built using FastAPI, following a service-oriented architecture.
Key components include:
- Intent Service: Leverages OpenAI to parse user input and determine underlying intent.
- Action Service: Executes specific business logic and operations based on identified intents.
- Session Manager: Maintains state and context across multiple user interactions.

*File Purpose (app.py):
This file serves as the main entry point for the backend application. It initializes the
FastAPI instance, configures CORS middleware for cross-origin requests, and defines the
primary API endpoints that orchestrate the flow between file processing, LLM-driven
intent analysis, and action execution.

*Endpoints Overview:
- /intent-parser: Handles voice-based user input and processes it through the intent service.
- /invoices/{invoice_id}/confirm: Updates the status of an invoice in the database.
- /export/inventory: Generates an Excel file containing the current inventory.
- /export/invoice/{invoice_id}: Generates a PDF file containing a specific invoice.
- /export/invoice-excel/{invoice_id}: Generates an Excel file containing a specific invoice.
- /whatsapp: Handles WhatsApp webhook requests and processes them through the intent service.
- /workflow/draft: Creates a new workflow draft based on a user prompt.
- /workflow/execute: Executes a workflow based on a user prompt.
- /workflows: Lists all workflows for a user.
- /workflows/{workflow_id}: Gets a specific workflow details.
- /workflow/save: Saves a workflow to the database.
- /webhooks/{service_name}: Dispatches webhook requests to the appropriate workflow.

*file structure:
- app.py: Main entry point for the backend application.
- services: Contains the service-oriented architecture components.
- lib: Contains the library functions and configurations.
- agents: Contains the agent-oriented architecture components.
- workflows: Contains the workflow-oriented architecture components.
- schemas: Contains the schema definitions for the data models.
- tests: Contains the test cases for the application.
- docs: Contains the documentation for the application.

"""

# imports
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from openai import OpenAI
from services.action_service import action_service
from services.intent_service import intent_service, session_manager
from dotenv import load_dotenv
from lib.supabase_lib import supabase
from lib.twilio_config import verify_twilio
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from agents.architect import WorkflowArchitect
from workflows.engine import inngest_client, execute_workflow
from inngest import Event
from inngest.fast_api import serve
from fastapi import Request
from workflows.schema import WorkflowBlueprint
from lib.supabase_lib import get_active_workflows_by_trigger
from webhooks.instagram import router as instagram_router
from routers.messages import router as messages_router
from services.sync_service import sync_service
import asyncio

# config
load_dotenv()
app = FastAPI(title="Bharat Biz-Agent API")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instagram_router)
app.include_router(messages_router)


async def background_sync_task():
    """Background task to poll for new messages every 60 seconds"""
    while True:
        try:
            print("🔄 Running background sync for social platforms...")
            await sync_service.sync_all()
        except Exception as e:
            print(f"❌ Background sync error: {e}")
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    # Start the background sync task
    asyncio.create_task(background_sync_task())


"""
This endpoint serves as the primary voice interface for the application, converting speech into actionable business logic.
Core Logic:
1. Transcription(speech-->text): Utilizes OpenAI's Whisper model to convert the uploaded audio file into text.
2. Intent Analysis(text-->valuable_info): Processes the transcribed text through the `intent_service` to identify the user's intent and extract relevant entities.
3. Session Management(saving_context): Employs the `session_manager` to maintain conversation state, enabling multi-turn dialogues and context-aware responses.
4. Action Execution(valuable_info-->action): Triggers the `action_service` to perform specific business operations (e.g., database updates, external API calls) based on the identified intent.
5. Multi-lingual Support:
"""


@app.post("/intent-parser")
async def intent_parser(
    audio_file: UploadFile = File(
        ...
    ),  # this audio file comes in form of form-data in the request (blob)
    session_id: str = Form("default_user"),
    user_lang: str = Form("Marathi"),  # Added language selection from frontend
):
    if not audio_file.content_type.startswith(
        "audio/"
    ):  # this is a validation check to ensure the uploaded file is an audio file
        raise HTTPException(status_code=400, detail="Invalid audio format")

    temp_path = f"temp_{audio_file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # 1. FORCE CLOSE and RE-OPEN (Essential for Windows)
        # TRANSCRIPTION AND TRANSLATION OF AUDIO FILE TO TEXT
        with open(temp_path, "rb") as audio_file_object:
            print(f"--- Starting Transcription for {temp_path} ---")

            try:
                # 2. Call Whisper
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file_object,
                    language="en",
                )
                raw_text = transcript.text.strip()
                print(f"--- Transcription Success: {raw_text} ---")

            except Exception as e:
                print(f"!!! Whisper Error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Whisper failed: {str(e)}")

        # CONTEXTUAL PROCESSING
        existing_memory = session_manager.get_session(session_id)
        print(
            f"--- Existing Memory: {existing_memory.model_dump_json() if existing_memory else 'None'} ---"
        )
        context = f"Existing Memory: {existing_memory.model_dump_json() if existing_memory else 'None'}. New Voice: {raw_text}"

        # 3. openAI Processing (Handles Local Language Response) (GIVES INTENT)
        result = await intent_service.parse_message(context, language=user_lang)
        # The 'result' is a Pydantic object containing 4 parameters:
        # 1. intent (str): The detected user goal or action.
        # 2. parameters (dict): Key-value pairs of extracted entities/data.
        # 2.5 data: optional but contains core for running execution funtions
        # 3. missing_info (list): A list of strings identifying required fields not yet provided.
        # 4. response (str): The translated/localized response text for the user.
        print(f"--- Result: {result.model_dump_json() if result else 'None'} ---")

        # 4. Save or Clear Session (SAVE CONTEXT if THE SYSTEM AS TO ASK FOOLOW-UP QUESTIONS)
        if result.missing_info:
            # If data is missing, save state and ask follow-up (SAVE CONTEXT)
            session_manager.save_session(session_id, result)
            # DEBUGGING: JSON Response for Missing Info
            # {
            #   "status": "pending",
            #   "reply": "Could you please provide the item names?"
            # }
            return {"status": "pending", "reply": result.response_text}

        # ACTION EXECUTION
        try:
            if not result.data:
                raise ValueError("Intent data is missing from the response")

            # INTENT TYPE CHECKING
            if result.intent_type == "CREATE_INVOICE":
                # VALIDATION CHECK: Ensure mandatory fields are actually there
                if (
                    not result.data
                    or not hasattr(result.data, "customer_name")
                    or not result.data.customer_name
                    or not result.data.items
                ):
                    print(
                        f"!!! Validation Error: Incomplete Invoice Data: {result.data}"
                    )
                    # DEBUGGING: JSON Response for Validation Error
                    # {
                    #   "status": "pending",
                    #   "reply": "I'm sorry...",
                    #   "analysis": { ... UserIntent dict ... }
                    # }
                    return {
                        "status": "pending",
                        "reply": "I'm sorry, I seem to have lost the invoice details. Could you please repeat what you want to bill?",
                        "analysis": result.model_dump(),
                    }

                # --- SMART PRICE CHECK LOGIC ---
                # Check if Paid Amount is explicitly valid or needs clarification "Discount vs Due"
                # Only check if amount_paid is provided and we can calculate a DB total
                if (
                    result.data.amount_paid is not None
                    and result.data.amount_paid > 0
                    and not result.data.discount_applied
                    and not result.data.is_due
                ):
                    calc = await action_service.calculate_potential_total(
                        result.data.items
                    )
                    db_total = calc["total"]

                    # If discrepancy exists (Paid provided < DB Total Estimate)
                    # Allow small margin of error (e.g. 1.0) for float diffs
                    if db_total > (result.data.amount_paid + 5.0):  # 5rs buffer
                        # Discrepancy Found!
                        # We need to ASK the user.
                        # Update Missing Info to "Clarification"
                        result.missing_info = ["Clarification: Discount or Due"]
                        diff_val = db_total - result.data.amount_paid
                        result.response_text = (
                            f"The standard price for these items is approx Rs. {db_total}, but you mentioned Rs. {result.data.amount_paid}. "
                            f"Is the remaining Rs. {diff_val} a Discount or is it Due?"
                        )

                        # Save session so next reply can answer "It is Due" or "Discount"
                        session_manager.save_session(session_id, result)

                        # MASK the intent so Frontend doesn't show the Invoice Draft yet
                        # We make a copy of the dump
                        analysis_dump = result.model_dump()
                        analysis_dump["intent_type"] = "CLARIFICATION_NEEDED"

                        return {
                            "status": "pending",
                            "reply": result.response_text,
                            "analysis": analysis_dump,
                        }

                # IF ALL THE DATA IS THERE
                action_data = await action_service.execute_invoice(result.data)

                if action_data.get("status") == "error":
                    print(f"!!! execute_invoice Error: {action_data.get('message')}")
                    raise Exception(
                        action_data.get("message", "Unknown error creating invoice")
                    )

                reply = f"Invoice created successfully for {result.data.customer_name}."

            elif result.intent_type == "CHECK_STOCK":
                stock = await action_service.get_stock(result.data.product_name)
                if stock["found"]:
                    reply = f"You have {stock['stock']} units of {stock['name']} left."
                else:
                    reply = f"Sorry, I couldn't find {result.data.product_name} in your inventory."
                stock_data = stock

            elif result.intent_type == "RECORD_PAYMENT":
                pay_res = await action_service.record_payment(
                    result.data.customer_name, result.data.amount
                )
                if pay_res.get("status") == "error":
                    raise Exception(
                        pay_res.get("message", "Unknown error recording payment")
                    )
                reply = f"Recorded payment of {result.data.amount} from {result.data.customer_name}."

            elif result.intent_type == "GENERATE_REPORT":
                download_url = "/export/inventory"
                reply = f"Report generated successfully. Download here: {download_url}"

            elif result.intent_type == "PAYMENT_REMINDER":
                if result.data.customer_name.upper() == "ALL":
                    debtors = await action_service.get_all_debtors()
                    if debtors.get("status") == "error":
                        raise Exception(
                            debtors.get("message", "Error fetching debtors")
                        )

                    # Also get overall business totals for the Outstanding Balance card
                    ledger = await action_service.get_overall_ledger()
                    if ledger.get("status") == "error":
                        raise Exception(
                            ledger.get("message", "Error fetching overall ledger")
                        )

                    if not debtors["data"]:
                        reply = "Great news! No one owes you any money right now."
                    else:
                        debt_list = "\n".join(
                            [
                                f"- {d['full_name']}: Rs. {d['total_debt']}"
                                for d in debtors["data"]
                            ]
                        )
                        reply = (
                            f"Here is the list of people who owe money:\n{debt_list}"
                        )
                else:
                    ledger = await action_service.get_customer_ledger(
                        result.data.customer_name
                    )
                    if ledger.get("status") == "error":
                        raise Exception(
                            ledger.get("message", "Unknown error fetching ledger")
                        )

                    reply = f"{ledger['customer']} owes a balance of {ledger['balance_due']}."

            else:
                reply = result.response_text

            """
            - CLEAR THE SESSION AFTER THE ACTION IS EXECUTED
            - CONSTRUCT THE FINAL RESPONSE
            - INJECT THE ACTION DATA INTO THE ANALYSIS DATA
            - INJECT THE STOCK DATA INTO THE ANALYSIS DATA
            - RETURN THE FINAL RESPONSE
            """
            # SUCCESS & CLEANUP
            session_manager.clear_session(session_id)

            # CONSTRUCT THE FINAL RESPONSE
            final_response = {
                "status": "success",
                "reply": reply,
                "analysis": result.model_dump(),  # CONVERT TO DICT
            }
            """
            - INJECT THE ACTION DATA INTO THE ANALYSIS DATA
            - INJECT THE STOCK DATA INTO THE ANALYSIS DATA
            """
            # VERIFY IF WE HAVE ACTION_DATA WITH ID
            if result.intent_type == "CREATE_INVOICE" and "action_data" in locals():
                if "invoice_id" in action_data:
                    # INJECT INTO THE ANALYSIS DATA DICT
                    if final_response["analysis"].get("data"):
                        final_response["analysis"]["data"]["invoice_id"] = action_data[
                            "invoice_id"
                        ]
                        # NEW: Inject the Enriched Items with Prices back to the Frontend
                        # The Frontend likely renders 'result.data.items'.
                        # We need to overwrite that specific part.
                        if "items" in action_data:
                            final_response["analysis"]["data"]["items"] = action_data[
                                "items"
                            ]

            # INJECT STOCK DATA IF PRESENT
            if result.intent_type == "CHECK_STOCK" and "stock_data" in locals():
                if final_response["analysis"].get("data"):
                    final_response["analysis"]["data"].update(stock_data)

            # INJECT LEDGER DATA IF PRESENT (for PAYMENT_REMINDER)
            if result.intent_type == "PAYMENT_REMINDER":
                if "ledger" in locals() and final_response["analysis"].get("data"):
                    # Inject ledger totals (works for both single customer and ALL)
                    final_response["analysis"]["data"].update(ledger)
                if "debtors" in locals() and final_response["analysis"].get("data"):
                    # All debtors list
                    final_response["analysis"]["data"]["debtors"] = debtors.get(
                        "data", []
                    )

            # RETURN THE FINAL RESPONSE
            # DEBUGGING: JSON Response for Success
            # {
            #   "status": "success",
            #   "reply": "Invoice created...",
            #   "analysis": {
            #       "internal_thought": "...",
            #       "intent_type": "CREATE_INVOICE",
            #       "confidence": 0.95,
            #       "data": {
            #           "customer_name": "...",
            #           "items": [...],
            #           "amount_paid": ...,
            #           "invoice_id": "123" // Injected
            #       },
            #       "missing_info": [],
            #       "response_text": "..."
            #   }
            # }
            return final_response

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Action Failed: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.patch("/invoices/{invoice_id}/confirm")
async def confirm_invoice(invoice_id: str):
    # Update the status in Supabase
    supabase.table("invoices").update({"status": "active"}).eq(
        "id", invoice_id
    ).execute()

    return {"status": "success", "message": "Invoice is now active and added to ledger"}


@app.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    try:
        # Delete the invoice.
        # Note: If cascade delete is set up in Supabase, this will auto-delete items/payments.
        # If not, we might need to delete children first.
        # Assuming cascade or standard deletion for now.

        # 1. Check if invoice exists (Optional, but good for validation)
        # 2. Perform Delete

        print(f"--- Deleting Invoice: {invoice_id} ---")

        # 1. Fetch Invoice Details to reverse the debt!
        inv_data = getattr(
            supabase.table("invoices")
            .select("customer_id, total_amount, amount_paid")
            .eq("id", invoice_id)
            .single(),
            "execute",
        )()
        if inv_data.data:
            cust_id = inv_data.data["customer_id"]
            tot = float(inv_data.data["total_amount"] or 0)
            paid = float(inv_data.data["amount_paid"] or 0)
            due_to_reverse = tot - paid

            # Subtract from customer total_debt
            if due_to_reverse != 0:
                cust_res = getattr(
                    supabase.table("customers")
                    .select("total_debt")
                    .eq("id", cust_id)
                    .single(),
                    "execute",
                )()
                curr_debt = float(cust_res.data.get("total_debt") or 0)
                getattr(
                    supabase.table("customers")
                    .update({"total_debt": curr_debt - due_to_reverse})
                    .eq("id", cust_id),
                    "execute",
                )()
                print(
                    f"DEBUG: Reversed Debt for {cust_id}: {curr_debt} -> {curr_debt - due_to_reverse}"
                )

        # 2. Manually delete invoice_items
        getattr(
            supabase.table("invoice_items").delete().eq("invoice_id", invoice_id),
            "execute",
        )()

        supabase.table("invoices").delete().eq("id", invoice_id).execute()

        return {"status": "success", "message": "Invoice deleted successfully"}

    except Exception as e:
        print(f"!!! Error deleting invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# in app end-pt
@app.get("/export/inventory")
async def export_inventory():
    """Download current inventory as Excel."""
    file_data = await action_service.generate_inventory_excel()
    return Response(
        content=file_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory.xlsx"},
    )


@app.get("/export/invoice/{invoice_id}")
async def export_invoice_pdf(invoice_id: str):
    """Download a specific invoice as PDF."""
    pdf_bytes = await action_service.generate_invoice_pdf(invoice_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
        },
    )


@app.get("/export/invoice-excel/{invoice_id}")
async def export_invoice_excel(invoice_id: str):
    """Download a specific invoice as Excel."""
    file_data = await action_service.generate_invoice_excel(invoice_id)
    return Response(
        content=file_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.xlsx"
        },
    )


# whatsapp webhook (uses twilio & intent-parser logic)
@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...), From: str = Form(...), _=Depends(verify_twilio)
):
    # 1. 'Body' is the text message (e.g., "Add 10kg sugar for Rahul")
    # 2. 'From' is the sender's WhatsApp number, which we use as session_id
    session_id = From
    raw_text = Body
    print(raw_text)
    # 1.5 LOGGING: Save to Supabase so it shows in Frontend
    # Remove 'whatsapp:' prefix for cleaner display if desired, or keep it.
    # The session_id usually comes as 'whatsapp:+91...' matching the 'From' field.
    try:
        # Upsert Session
        supabase.table("sessions").upsert(
            {
                "platform": "whatsapp",
                "external_id": session_id,
                "is_bot_active": True,  # Default to true
                "updated_at": "now()",
            },
            on_conflict="platform, external_id",
        ).execute()

        # Get the integer ID of the session
        session_res = (
            supabase.table("sessions")
            .select("id")
            .eq("platform", "whatsapp")
            .eq("external_id", session_id)
            .single()
            .execute()
        )

        if session_res.data:
            db_session_id = session_res.data["id"]

            # Log Incoming Message
            supabase.table("unified_messages").insert(
                {
                    "session_id": db_session_id,
                    "platform": "whatsapp",
                    "direction": "inbound",
                    "content": raw_text,
                    "sender_handle": session_id,
                    "status": "received",
                }
            ).execute()
    except Exception as e:
        print(f"!!! Error logging WhatsApp message to DB: {e}")

    # 2. Contextual Processing
    existing_memory = session_manager.get_session(session_id)
    context = (
        f"Existing Memory: {existing_memory.model_dump_json() if existing_memory else 'None'}. "
        f"New Voice: {raw_text}"
    )

    # 3. openAI Processing (Handles Local Language Response)
    # Defaulting to English for WhatsApp for now
    result = await intent_service.parse_message(context, language="English")

    # 4. Save or Clear Session
    if result.missing_info:
        # If data is missing, save state and ask follow-up
        session_manager.save_session(session_id, result)
        reply = result.response_text
    else:
        # If no info is missing, execute the specific action
        try:
            if not result.data:
                raise ValueError("Intent data is missing from the response")

            if result.intent_type == "CREATE_INVOICE":
                # Robustness check: Ensure mandatory fields are actually there
                if (
                    not result.data
                    or not hasattr(result.data, "customer_name")
                    or not result.data.customer_name
                    or not result.data.items
                ):
                    print(
                        f"!!! Validation Error: Incomplete Invoice Data: {result.data}"
                    )
                    reply = "I'm sorry, I seem to have lost the invoice details. Could you please repeat what you want to bill?"
                else:
                    action_data = await action_service.execute_invoice(result.data)
                    if action_data.get("status") == "error":
                        print(
                            f"!!! execute_invoice Error: {action_data.get('message')}"
                        )
                        raise Exception(
                            action_data.get("message", "Unknown error creating invoice")
                        )
                    reply = (
                        f"Invoice created successfully for {result.data.customer_name}."
                    )

            elif result.intent_type == "CHECK_STOCK":
                stock = await action_service.get_stock(result.data.product_name)
                if stock["found"]:
                    reply = f"You have {stock['stock']} units of {stock['name']} left."
                else:
                    reply = f"Sorry, I couldn't find {result.data.product_name} in your inventory."

            elif result.intent_type == "RECORD_PAYMENT":
                pay_res = await action_service.record_payment(
                    result.data.customer_name, result.data.amount
                )
                if pay_res.get("status") == "error":
                    raise Exception(
                        pay_res.get("message", "Unknown error recording payment")
                    )
                reply = f"Recorded payment of {result.data.amount} from {result.data.customer_name}."

            elif result.intent_type == "GENERATE_REPORT":
                download_url = "/export/inventory"
                reply = f"Report generated successfully. Download here: {download_url}"

            elif result.intent_type == "PAYMENT_REMINDER":
                ledger = await action_service.get_customer_ledger(
                    result.data.customer_name
                )
                if ledger.get("status") == "error":
                    raise Exception(
                        ledger.get("message", "Unknown error fetching ledger")
                    )
                reply = (
                    f"{ledger['customer']} owes a balance of {ledger['balance_due']}."
                )
            else:
                reply = result.response_text

            # 3. Success & Cleanup
            session_manager.clear_session(session_id)

        except Exception as e:
            reply = f"Action Failed: {str(e)}"

    # 5. Respond back to the user on WhatsApp
    resp = MessagingResponse()
    resp.message(reply)

    # 5.5 LOGGING: Save the OUTGOING reply to Supabase
    try:
        if "db_session_id" in locals():
            supabase.table("unified_messages").insert(
                {
                    "session_id": db_session_id,
                    "platform": "whatsapp",
                    "direction": "outbound",
                    "content": reply,
                    "sender_handle": "AI Assistant",
                    "status": "sent",
                }
            ).execute()
    except Exception as e:
        print(f"!!! Error logging WhatsApp reply to DB: {e}")

    return Response(content=str(resp), media_type="application/xml")


# ---------------------------------------------------------------------> WORKFLOW AUTOMATION <---------------------------------------------------
"""
WORKFLOW AUTOMATION ENGINE OVERVIEW
-----------------------------------
This section handles the dynamic creation, management, and execution of business workflows.
It utilizes three core technologies:
1. LangChain / OpenAI: For the 'WorkflowArchitect' which turns natural language into JSON blueprints.
2. Supabase: For persisting blueprints (`workflow_blueprints`) and execution logs.
3. Inngest: A serverless queue/engine that handles the actual step-by-step execution and retries.

DB Structure (Supabase - workflow_blueprints):
- id (uuid): Primary Key.
- user_id (text): Links the workflow to a specific user.
- name (text): Human-readable name (e.g., "AI Draft: Invoice notification").
- nodes (jsonb): Array of React Flow compatible node objects (id, type, data, position).
- edges (jsonb): Array of React Flow compatible edge objects (id, source, target).
- is_active (bool): Whether the workflow is currently ready for execution.
"""
architect = WorkflowArchitect()


# fully working
@app.post("/workflow/draft")
async def create_draft(prompt: str = Query(...), user_id: str = Query(...)):
    """
    PURPOSE: Converts a user's natural language wish into a structured graph theory (Nodes/Edges).

    RECEIVES:
    - prompt (str): The raw text from the user (e.g., "When I get an order, send a WhatsApp").
    - user_id (str): The owner of this workflow.

    LOGIC:
    1. Pass the prompt to `WorkflowArchitect`.
    2. Architect uses LLM + Tool calling to generate a valid JSON blueprint (nodes/edges).
    3. The blueprint is saved to 'workflow_blueprints' with `is_active=False`.

    RETURNS:
    - workflow_id: The ID of the newly created draft.

    FRONTEND IMPACT:
    The frontend should redirect to the Canvas and load this ID to let the user "see" their automation.
    """
    print("🚀 [/workflow/draft] Endpoint hit")
    print(f"📝 [/workflow/draft] Prompt received: {prompt}")
    print(f"👤 [/workflow/draft] User ID: {user_id}")

    # 1. Ask LangChain to build the JSON
    print("🤖 [/workflow/draft] Calling architect.draft_workflow()")
    blueprint_obj = await architect.draft_workflow(prompt)

    # 2. Convert the Pydantic/LangChain object to a plain Python Dictionary
    blueprint_json = blueprint_obj.model_dump()
    print(f"📊 [/workflow/draft] Blueprint JSON: {blueprint_json}")

    # 3. Save it to Supabase so the Frontend can load it
    print("💾 [/workflow/draft] Inserting into Supabase workflow_blueprints table")
    result = (
        supabase.table("workflow_blueprints")
        .insert(
            {
                "user_id": user_id,
                "name": f"AI Draft: {prompt[:20]}...",
                "nodes": blueprint_json["nodes"],
                "edges": blueprint_json["edges"],
                "is_active": False,  # User needs to review it first!
            }
        )
        .execute()
    )

    workflow_id = result.data[0]["id"]
    return {"status": "success", "workflow_id": workflow_id}


@app.post("/workflow/execute")
async def execute_workflow_endpoint(blueprint: WorkflowBlueprint, payload: dict = None):
    """
    PURPOSE: Manually triggers a specific workflow execution.

    RECEIVES:
    - blueprint (WorkflowBlueprint): The full graph (nodes/edges) representing the code to run.
    - payload (dict): Optional external data (like an order object) to inject into the workflow.

    LOGIC:
    1. Generates a unique `run_id` for tracking.
    2. Packages the blueprint and payload into an Inngest Event.
    3. Handoff: `inngest_client.send` puts this on a queue. The `execute_workflow` function
       in Python then takes over asynchronously.

    RETURNS:
    - run_id: Used for monitoring progress in real-time.
    """
    print("\n" + "=" * 60)
    print("▶️ [/workflow/execute] Endpoint hit")

    import uuid

    run_id = str(uuid.uuid4())
    print(f"🆔 [/workflow/execute] Generated run_id: {run_id}")

    # Send event to Inngest to start the workflow
    # This triggers the 'execute_workflow' logic in backend/app/workflows/engine.py
    print("📡 [/workflow/execute] Sending event to Inngest")
    await inngest_client.send(
        Event(
            name="workflow/run_requested",
            data={
                "blueprint": blueprint.model_dump(mode="json"),
                "payload": payload or {},
            },
        )
    )
    print("✅ [/workflow/execute] Event sent to Inngest")
    print("=" * 60 + "\n")

    return {"status": "success", "run_id": run_id}


# ---------------------------------------------------------------------> CORE WORKFLOW ENDS ABOVE <---------------------------------------------------


@app.get("/workflows")
async def list_workflows(user_id: str = Query(...)):
    """
    PURPOSE: Fetches all workflows saved by a specific user.
    RECEIVES: user_id (str)
    LOGIC: Queries 'workflow_blueprints' table filter by 'user_id'.
    RETURNS: List of workflow objects.
    """
    print(f"\n📋 [/workflows] Listing workflows for user: {user_id}")

    try:
        result = (
            supabase.table("workflow_blueprints")
            .select("id, name, created_at, is_active, nodes, edges")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return {"status": "success", "workflows": result.data}

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch workflows: {str(e)}")


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, user_id: str = Query(...)):
    """
    PURPOSE: Loads a single workflow's full blueprint (nodes/edges).
    RECEIVES: workflow_id (path), user_id (query)
    LOGIC: Primary key lookup in 'workflow_blueprints'.
    RETURNS: The single workflow object.
    """
    try:
        result = (
            supabase.table("workflow_blueprints")
            .select("*")
            .eq("id", workflow_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        return {"status": "success", "workflow": result.data}

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch workflow: {str(e)}")


@app.post("/workflow/save")
async def save_workflow(
    blueprint: WorkflowBlueprint,
    user_id: str = Query(...),
    workflow_name: str = Query(...),
):
    """
    PURPOSE: Finalizes a draft or updates an existing workflow to be 'Active'.

    RECEIVES:
    - blueprint: Modified nodes/edges from the Frontend Canvas.
    - user_id: Owner ID.
    - workflow_name: What to call this automation.

    LOGIC:
    1. Validation: Ensures the workflow actually has logic (nodes).
    2. Storage: Inserts or Updates the record in Supabase with `is_active=True`.

    RETURNS: The newly inserted/updated database record ID.
    """
    print("� [/workflow/save] Saving workflow...")

    try:
        # Validate blueprint
        if not blueprint.nodes:
            raise HTTPException(400, "Workflow must have at least one node")

        # Convert pydantic models to dict for JSONB storage
        blueprint_data = {
            "user_id": user_id,
            "name": workflow_name,
            "nodes": [node.dict() for node in blueprint.nodes],
            "edges": [edge.dict() for edge in blueprint.edges],
            "is_active": True,
        }

        result = supabase.table("workflow_blueprints").insert(blueprint_data).execute()
        workflow_id = result.data[0]["id"]

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": "Workflow saved successfully!",
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to save workflow: {str(e)}")


@app.post("/webhooks/generic/{service_name}")
async def generic_webhook_dispatcher(service_name: str, request: Request):
    """
    PURPOSE: The 'Magic Bridge' between external apps and our workflows.

    RECEIVES:
    - service_name (e.g., 'razorpay', 'instagram', 'whatsapp'): From URL.
    - JSON Payload: From the service's webhook request body.

    LOGIC:
    1. DECOUPLING: We don't write service-specific code here. Instead...
    2. TRIGGER LOOKUP: We look in our DB for ANY active workflow whose first node (trigger)
       matches this `service_name`.
    3. ASYNC HANDOFF: For every match, we fire an Inngest event.

    WHY THIS IS COOL:
    A user can "add Instagram integration" just by dragging an Instagram node in the UI.
    The backend dispatcher will automatically start finding and running that workflow
    without any redeployment.
    """

    # 1. Capture the data sent by the service
    payload = await request.json()

    # 2. Find all active workflows that start with this service
    # This queries supabase for: is_active=True AND first_node_type == service_name
    blueprints = get_active_workflows_by_trigger(service_name)

    if not blueprints:
        return {"status": "ignored", "reason": f"No active workflow for {service_name}"}

    # 3. For every matching workflow, tell Inngest to START
    for blueprint in blueprints:
        await inngest_client.send(
            Event(
                name="workflow/run_requested",
                data={
                    "blueprint": blueprint,
                    "payload": payload,  # This becomes 'trigger_data' in our engine
                },
            )
        )

    return {"status": "dispatched", "count": len(blueprints)}


# Serve Inngest functions properly
# This exposes a '/api/inngest' endpoint which the Inngest Dev Server polls to
# find out what functions (like execute_workflow) are available to run.
serve(app, inngest_client, [execute_workflow])
