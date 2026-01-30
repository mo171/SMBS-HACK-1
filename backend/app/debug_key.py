from dotenv import load_dotenv
import os
import google.genai as genai

# Force reload of environment variables
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print(f"Loaded API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found!")
    exit(1)

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello",
    )
    print("✅ API Call Successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ API Call Failed: {e}")
