import os, requests, re
from flask import Flask, request
from supabase import create_client

app = Flask(__name__)

# ===== SEMUA UDAH DIISIIN =====
WABLAS_TOKEN = "xZ5MopMIM3hgKRvDFLiROS2r1N6E0HDebyky2YiW0cKup3XqSIBy04D"
SUPABASE_URL = "https://mzcuyneiufvttafdkgyr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16Y3V5bmVpdWZ2dHRhZmRrZ3lyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE0NzYwNTcsImV4cCI6MjA5NzA1MjA1N30.JnxrNzgVDegr-6gWh11wIZVpe6A9KYfO8zkpBoLuKmA"
ADMIN_FEE = 1000
# ==============================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_wa(phone, message):
    url = "https://texas.wablas.com/api/send-message"
    headers = {
        "Authorization": WABLAS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "phone": phone,
        "message": message
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"WABLAS: {res.status_code} | {res.text}")
    except Exception as e:
        print(f"WABLAS ERROR: {e}")

def extract_amount(text):
    match = re.search(r'(?:Rp\.?\s?)?(\d{1,3}(?:[.,]\d{3})+|\d+)', text)
    if match:
        return int(re.sub(r'[.,]', '', match.group(1)))
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("DATA WABLAS:", data)
        
        sender = data.get('sender', '')
        phone = data.get('phone', '')
        from_me = data.get('fromMe', False)
        message = data.get('message', '')
        pushname = data.get('pushName', 'User')
        
        print(f"SENDER: {sender} | PHONE: {phone} | FROM_ME: {from_me} | MSG: {message}")
        
        if from_me:
            return "ok", 200
        
        target_phone = phone.replace("@c.us", "").replace("@s.whatsapp.net", "")
        
        if not target_phone:
            print("GAK ADA NOMOR PENGIRIM")
            return "ok", 200
            
        send_wa(target_phone, f"Test bot. Lo kirim: {message}")
        return "ok", 200
        
    except Exception as e:
        print(f"ERROR WEBHOOK: {e}")
        return "ok", 200

if __name__ == "__main__":
    app.run()
