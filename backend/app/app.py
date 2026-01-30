from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import shutil
from openai import OpenAI
from services.action_service import action_service
from services.intent_service import intent_service, session_manager

load_dotenv()

app = FastAPI(title="Bharat Biz-Agent API")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {"message": "Bharat Biz-Agent API is running"}


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

        # 1. Transcribe (NOT Translate) - Keeps Marathi script
        with open(temp_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                # Setting language ensures Whisper doesn't try to translate to English
                language="mr" if user_lang.lower() == "marathi" else "hi",
            )

        raw_text = transcript.text.strip()

        # 2. Contextual Processing
        existing_memory = session_manager.get_session(session_id)
        context = f"Existing Memory: {existing_memory.model_dump_json() if existing_memory else 'None'}. New Voice: {raw_text}"

        # 3. Gemini Processing (Handles Local Language Response)
        result = await intent_service.parse_message(context, language=user_lang)

        # 4. Save or Clear Session
        # Inside your app.py route:
        if result.intent_type == "CHECK_STOCK":
            product_to_check = result.data.product_name
            stock_info = await action_service.get_stock(product_to_check)

            if stock_info["found"]:
                # Update the AI's response with the REAL number from the DB
                final_reply = f"You have {stock_info['stock']} units of {stock_info['name']} in stock."
            else:
                final_reply = (
                    f"I couldn't find {product_to_check} in your inventory list."
                )

            return {"status": "complete", "reply": final_reply, "data": stock_info}

        if not result.missing_info and result.intent_type == "CREATE_INVOICE":
            # Optional: Save immediately as a 'Draft'
            db_status = await action_service.execute_invoice(result.data)

            session_manager.clear_session(session_id)
            return {
                "status": "complete",
                "reply": result.response_text,
                "invoice_details": result.data,
                "db_record": db_status,
            }
        else:
            session_manager.save_session(session_id, result)
            return {
                "status": "pending",
                "reply": result.response_text,
                "missing": result.missing_info,
            }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
