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


@app.post("/intent-parser")
async def intent_parser(
    audio_file: UploadFile = File(...),
    session_id: str = Form("default_user"),
    user_lang: str = Form("Marathi"),  # Added language selection from frontend
):
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    temp_path = f"temp_{audio_file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # 1. FORCE CLOSE and RE-OPEN (Essential for Windows)
        # This ensures the 'write' lock is released before OpenAI tries to 'read'
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

        # 2. Contextual Processing
        existing_memory = session_manager.get_session(session_id)
        context = f"Existing Memory: {existing_memory.model_dump_json() if existing_memory else 'None'}. New Voice: {raw_text}"

        # 3. openAI Processing (Handles Local Language Response)
        result = await intent_service.parse_message(context, language=user_lang)

        # 4. Save or Clear Session
        if result.missing_info:
            # If data is missing, save state and ask follow-up
            session_manager.save_session(session_id, result)
            return {"status": "pending", "reply": result.response_text}

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
                    return {
                        "status": "pending",
                        "reply": "I'm sorry, I seem to have lost the invoice details. Could you please repeat what you want to bill?",
                        "analysis": result.model_dump(),
                    }

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

            # 3. Success & Cleanup
            session_manager.clear_session(session_id)

            # Construct final response
            final_response = {
                "status": "success",
                "reply": reply,
                "analysis": result.model_dump(),  # Convert to dict
            }

            # Verify if we have action_data with ID
            if result.intent_type == "CREATE_INVOICE" and "action_data" in locals():
                if "invoice_id" in action_data:
                    # Inject into the analysis data dict
                    if final_response["analysis"].get("data"):
                        final_response["analysis"]["data"]["invoice_id"] = action_data[
                            "invoice_id"
                        ]

            # Inject stock data if present
            if result.intent_type == "CHECK_STOCK" and "stock_data" in locals():
                if final_response["analysis"].get("data"):
                    final_response["analysis"]["data"].update(stock_data)

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


# In backend/app.py
@app.post("/workflow/save")
async def save_workflow(blueprint: WorkflowBlueprint, user_id: str):
    # 1. Convert the blueprint to a dictionary
    # 2. Store it in your 'workflow_blueprints' table in Supabase
    # 3. Mark it as 'active'
    return {"message": "Workflow is live!"}


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
