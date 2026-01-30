from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import shutil
from openai import OpenAI
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

@app.post("/intent-parser")
async def intent_parser(
    audio_file: UploadFile = File(...), 
    session_id: str = Form("default_user"),
    user_lang: str = Form("Marathi") # Added language selection from frontend
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
                language="mr" if user_lang.lower() == "marathi" else "hi" 
            )
        
        raw_text = transcript.text.strip()

        # 2. Contextual Processing
        existing_memory = session_manager.get_session(session_id)
        context = f"Existing Memory: {existing_memory.model_dump_json() if existing_memory else 'None'}. New Voice: {raw_text}"

        # 3. Gemini Processing (Handles Local Language Response)
        result = await intent_service.parse_message(context, language=user_lang)

        # 4. Save or Clear Session
        if not result.missing_info:
            session_manager.clear_session(session_id)
            return {"status": "complete", "reply": result.response_text, "data": result}
        else:
            session_manager.save_session(session_id, result)
            return {"status": "pending", "reply": result.response_text, "missing": result.missing_info}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)