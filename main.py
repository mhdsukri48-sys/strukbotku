from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

WABLAS_TOKEN = os.getenv("WABLAS_TOKEN")
WABLAS_SECRET = os.getenv("WABLAS_SECRET")

@app.post("/")
async def webhook(request: Request):
    body = await request.json()
    phone = body.get("phone")
    message = body.get("message", "").upper()
    
    print(f"PHONE: {phone} | FROM_ME: {body.get('isGroup')} | MSG: {message}")

    if message == "SALDO":
        payload = {
            "phone": phone,
            "message": "Saldo kamu: Rp 50,000"
        }
        headers = {
            "Authorization": f"{WABLAS_TOKEN}.{WABLAS_SECRET}"
        }
        r = requests.post(
            "https://texas.wablas.com/api/send-message",
            headers=headers,
            data=payload  # Pake data= bukan json=
        )
        print(f"WABLAS: {r.status_code} | {r.text}")

    return {"status": "ok"}

@app.get("/")
def home():
    return {"status": "Bot jalan bro"}
