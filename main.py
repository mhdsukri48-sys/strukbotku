from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

WABLAS_TOKEN = os.getenv("WABLAS_TOKEN")
WABLAS_SECRET = os.getenv("WABLAS_SECRET")

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    
    phone = data.get("phone")
    message = data.get("message", "").upper()
    is_from_me = data.get("is_from_me", False)
    
    print(f"PHONE: {phone} | FROM_ME: {is_from_me} | MSG: {message}")
    print(f"WABLAS_TOKEN: {WABLAS_TOKEN}")
    print(f"WABLAS_SECRET: {WABLAS_SECRET}")
    
    if not is_from_me and "SALDO" in message:
        payload = {
            "data": [{
                "phone": phone,
                "message": "Saldo kamu: Rp 50,000"
            }]
        }
        headers = {
            "Authorization": WABLAS_TOKEN,
            "Secret": WABLAS_SECRET,
            "Content-Type": "application/json"
        }
        r = requests.post(
            "https://jogja.wablas.com/api/v2/send-message",
            headers=headers,
            json=payload
        )
        print(f"WABLAS: {r.status_code} | {r.text}")
    
    return {"status": "ok"}

@app.get("/")
def home():
    return {"status": "Bot jalan bro"}
