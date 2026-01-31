import os
from twilio.request_validator import RequestValidator
from fastapi import Header, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

# Put your Twilio Auth Token in your .env file
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
validator = RequestValidator(TWILIO_AUTH_TOKEN)


async def verify_twilio(request: Request, x_twilio_signature: str = Header(None)):
    """Security check to ensure the request actually came from Twilio."""
    # Twilio signature validation requires the exact URL
    # When behind ngrok or a proxy, request.url might be local (http://127.0.0.1)
    # but Twilio signed the public ngrok URL.

    # 1. Get the real public URL (check for proxy headers)
    protocol = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    path = request.url.path
    query = f"?{request.url.query}" if request.url.query else ""

    public_url = f"{protocol}://{host}{path}{query}"

    form_data = await request.form()

    # In production, this ensures only Twilio can hit this route
    if not validator.validate(public_url, dict(form_data), x_twilio_signature):
        print(f"!!! Twilio Validation Failed for URL: {public_url}")
        raise HTTPException(status_code=403, detail="Invalid Signature")
