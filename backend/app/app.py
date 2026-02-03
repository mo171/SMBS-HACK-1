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
from workflows.engine import inngest_client
from fastapi import Request
from workflows.schema import WorkflowBlueprint
from lib.supabase_lib import get_active_workflows_by_trigger

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
    result = (
        supabase.table("invoices")
        .update({"status": "active"})
        .eq("id", invoice_id)
        .execute()
    )

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

        # FIX: Manually delete invoice_items first to avoid FK constraint violation
        # (Assuming 'invoice_items' has a FK to 'invoices.id')
        getattr(
            supabase.table("invoice_items").delete().eq("invoice_id", invoice_id),
            "execute",
        )()

        # Now delete the invoice
        res = getattr(
            supabase.table("invoices").delete().eq("id", invoice_id), "execute"
        )()

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


@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...), From: str = Form(...), _=Depends(verify_twilio)
):
    # 1. 'Body' is the text message (e.g., "Add 10kg sugar for Rahul")
    # 2. 'From' is the sender's WhatsApp number, which we use as session_id
    session_id = From
    raw_text = Body

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

    return Response(content=str(resp), media_type="application/xml")


architect = WorkflowArchitect()


@app.post("/workflow/draft")
async def create_draft(prompt: str = Query(...), user_id: str = Query(...)):
    print("\n" + "=" * 60)
    print("🚀 [/workflow/draft] Endpoint hit")
    print(f"📝 [/workflow/draft] Prompt received: {prompt}")
    print(f"👤 [/workflow/draft] User ID: {user_id}")

    # 1. Ask LangChain to build the JSON
    print("🤖 [/workflow/draft] Calling architect.draft_workflow()")
    blueprint_obj = await architect.draft_workflow(prompt)
    print(f"✅ [/workflow/draft] Blueprint object generated: {type(blueprint_obj)}")

    # 2. Convert the Pydantic/LangChain object to a plain Python Dictionary
    blueprint_json = blueprint_obj.model_dump()
    print(f"📊 [/workflow/draft] Blueprint JSON: {blueprint_json}")
    print(f"📊 [/workflow/draft] Nodes count: {len(blueprint_json.get('nodes', []))}")
    print(f"🔗 [/workflow/draft] Edges count: {len(blueprint_json.get('edges', []))}")

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
    print(f"✅ [/workflow/draft] Workflow saved with ID: {workflow_id}")
    print("=" * 60 + "\n")

    return {"status": "success", "workflow_id": workflow_id}


@app.post("/workflow/execute")
async def execute_workflow_endpoint(blueprint: WorkflowBlueprint, payload: dict = None):
    """
    Execute a workflow from the frontend and return run_id for monitoring.
    """
    print("\n" + "=" * 60)
    print("▶️ [/workflow/execute] Endpoint hit")
    print(f"📊 [/workflow/execute] Blueprint received: {blueprint}")
    print(f"📦 [/workflow/execute] Payload: {payload}")

    # Generate a unique run_id for this execution
    import uuid

    run_id = str(uuid.uuid4())
    print(f"🆔 [/workflow/execute] Generated run_id: {run_id}")

    # Send event to Inngest to start the workflow
    print("📡 [/workflow/execute] Sending event to Inngest")
    await inngest_client.send(
        "workflow/run_requested",
        data={
            "blueprint": blueprint.dict(),
            "payload": payload or {},
        },
    )
    print("✅ [/workflow/execute] Event sent to Inngest")
    print("=" * 60 + "\n")

    return {"status": "success", "run_id": run_id}


@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    payload = await request.json()

    # 1. Find the active blueprint in Supabase that matches this trigger
    # (Select from workflow_blueprints where trigger_service = 'razorpay')
    blueprint = {"nodes": [...], "edges": [...]}

    # 2. Tell Inngest to start the engine
    await inngest_client.send(
        "workflow/run_requested", data={"blueprint": blueprint, "payload": payload}
    )

    return {"status": "accepted"}


@app.get("/workflows")
async def list_workflows(user_id: str = Query(...)):
    """List all workflows for a user"""
    print(f"\n📋 [/workflows] Listing workflows for user: {user_id}")

    try:
        result = (
            supabase.table("workflow_blueprints")
            .select("id, name, created_at, is_active, nodes, edges")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        workflows = result.data
        print(f"✅ [/workflows] Found {len(workflows)} workflows")

        return {"status": "success", "workflows": workflows}

    except Exception as e:
        error_msg = f"Failed to fetch workflows: {str(e)}"
        print(f"❌ [/workflows] {error_msg}")
        raise HTTPException(500, error_msg)


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, user_id: str = Query(...)):
    """Get specific workflow details"""
    print(f"\n🔍 [/workflows/{workflow_id}] Fetching workflow for user: {user_id}")

    try:
        result = (
            supabase.table("workflow_blueprints")
            .select("*")
            .eq("id", workflow_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        workflow = result.data
        print(f"✅ [/workflows/{workflow_id}] Workflow found: {workflow['name']}")

        return {"status": "success", "workflow": workflow}

    except Exception as e:
        error_msg = f"Failed to fetch workflow: {str(e)}"
        print(f"❌ [/workflows/{workflow_id}] {error_msg}")
        raise HTTPException(500, error_msg)


# In backend/app.py
@app.post("/workflow/save")
async def save_workflow(
    blueprint: WorkflowBlueprint,
    user_id: str = Query(...),
    workflow_name: str = Query(...),
):
    print("\n" + "=" * 60)
    print("💾 [/workflow/save] Endpoint hit")
    print(f"👤 [/workflow/save] User ID: {user_id}")
    print(f"📝 [/workflow/save] Workflow name: {workflow_name}")
    print(f"📊 [/workflow/save] Blueprint: {blueprint}")

    try:
        # Validate blueprint
        if not blueprint.nodes:
            print("❌ [/workflow/save] No nodes in blueprint")
            raise HTTPException(400, "Workflow must have at least one node")

        print(f"📊 [/workflow/save] Nodes count: {len(blueprint.nodes)}")
        print(f"🔗 [/workflow/save] Edges count: {len(blueprint.edges)}")

        # Convert blueprint to dict for storage
        blueprint_data = {
            "user_id": user_id,
            "name": workflow_name,
            "nodes": [node.dict() for node in blueprint.nodes],
            "edges": [edge.dict() for edge in blueprint.edges],
            "is_active": True,
        }

        print("💾 [/workflow/save] Inserting into Supabase")
        result = supabase.table("workflow_blueprints").insert(blueprint_data).execute()

        workflow_id = result.data[0]["id"]
        print(f"✅ [/workflow/save] Workflow saved with ID: {workflow_id}")
        print("=" * 60 + "\n")

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": "Workflow saved successfully!",
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to save workflow: {str(e)}"
        print(f"❌ [/workflow/save] {error_msg}")
        print("=" * 60 + "\n")
        raise HTTPException(500, error_msg)


@app.post("/webhooks/{service_name}")
async def webhook_dispatcher(service_name: str, request: Request):
    # 1. Capture the data sent by the service (Razorpay/Instagram)
    payload = await request.json()

    # 2. Find all active workflows that start with this service
    blueprints = get_active_workflows_by_trigger(service_name)

    if not blueprints:
        return {"status": "ignored", "reason": f"No active workflow for {service_name}"}

    # 3. For every matching workflow, tell Inngest to START
    for blueprint in blueprints:
        await inngest_client.send(
            "workflow/run_requested",
            data={
                "blueprint": blueprint,
                "payload": payload,  # This becomes 'trigger_data' in our engine
            },
        )

    return {"status": "dispatched", "count": len(blueprints)}
