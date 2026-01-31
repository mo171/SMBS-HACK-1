import requests


def test_whatsapp_endpoint():
    url = "http://127.0.0.1:8000/whatsapp"
    data = {
        "Body": "Create invoice for John Doe for 5 apples",
        "From": "whatsapp:+1234567890",
    }

    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print("Response Body:")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_whatsapp_endpoint()
