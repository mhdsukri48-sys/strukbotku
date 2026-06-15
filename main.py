import os
import requests
from flask import Flask, request
from supabase import create_client, Client

print("SUPABASE_KEY:", os.environ.get("SUPABASE_KEY")[:15] + "...")
print("WABLAS_SECRET:", os.environ.get("WABLAS_SECRET")[:10] + "...")

app = Flask(__name__)

WABLAS_TOKEN = os.environ.get("WABLAS_TOKEN")
WABLAS_URL = "https://texas.wablas.com"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_wa(phone, text):
    url = f"{WABLAS_URL}/api/send-message"
    headers = {
        'Authorization': WABLAS_TOKEN,
        'Secret': os.environ.get("WABLAS_SECRET")
        'Content-Type': 'application/x-www-form-urlencoded' 
    }
    payload = {'phone': phone, 'message': text}
    res = requests.post(url, headers=headers, data=payload)
    print(f"WABLAS: {res.status_code} | {res.text}")

def get_saldo(phone):
    try:
        result = supabase.table("users").select("balance").eq("phone", phone).execute()
        if result.data:
            return result.data[0]['balance']
        return None
    except Exception as e:
        print(f"ERROR SUPABASE: {e}")
        return None

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("DATA WABLAS:", data)

        phone = data.get('phone', '').replace("@c.us", "").replace("@s.whatsapp.net", "")
        from_me = data.get('fromMe', False)
        message = data.get('message', '').strip().upper()

        print(f"PHONE: {phone} | FROM_ME: {from_me} | MSG: {message}")

        if from_me or not phone:
            return "ok", 200

        if message == "SALDO":
            saldo = get_saldo(phone)
            if saldo is not None:
                send_wa(phone, f"Saldo kamu: Rp {saldo:,}")
            else:
                send_wa(phone, "Nomor kamu belum terdaftar. Hubungi admin.")
        else:
            send_wa(phone, "Ketik SALDO untuk cek saldo kamu.")

        return "ok", 200

    except Exception as e:
        print(f"ERROR WEBHOOK: {e}")
        return "ok", 200

@app.route("/")
def home():
    return "Bot Aktif"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
