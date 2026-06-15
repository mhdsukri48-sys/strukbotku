import os, requests, re
from flask import Flask, request
from supabase import create_client

app = Flask(__name__)

# ===== SEMUA UDAH DIISIIN =====
WABLAS_TOKEN = "B6rzLrCIyvIdP39XPav6cWf2xWyUMKneZBjTjerwogsPJ6EItU"
SUPABASE_URL = "https://mzcuyneiufvttafdkgyr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16Y3V5bmVpdWZ2dHRhZmRrZ3lyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE0NzYwNTcsImV4cCI6MjA5NzA1MjA1N30.JnxrNzgVDegr-6gWh11wIZVpe6A9KYfO8"
ADMIN_FEE = 1000
# ==============================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_wa(phone, message):
    url = "https://texas.wablas.com/api/send-message"
    headers = {"Authorization": WABLAS_TOKEN}
    data = {"phone": phone, "message": message}
    requests.post(url, headers=headers, data=data)

def extract_amount(text):
    match = re.search(r'(?:Rp\.?\s?)?(\d{1,3}(?:[.,]\d{3})+|\d+)', text)
    if match:
        return int(re.sub(r'[.,]', '', match.group(1)))
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    phone = data['phone'].replace("@c.us", "")
    msg = data.get('message', '')
    
    user = supabase.table("users").select("*").eq("id", int(phone)).execute()
    if not user.data:
        supabase.table("users").insert({"id": int(phone), "name": data.get('pushName', 'User')}).execute()
        send_wa(phone, "Halo! Kirim foto struk + nominal buat topup saldo.\n\nCek saldo: ketik SALDO")
        return "ok"
    
    user_data = user.data[0]
    
    if msg.lower() in ['saldo', 'cek', 'balance']:
        send_wa(phone, f"Saldo kamu: Rp{user_data['balance']:,}")
        return "ok"
    
    amount = extract_amount(msg)
    if amount and amount >= 10000:
        total = amount - ADMIN_FEE
        receipt = supabase.table("receipts").insert({
            "user_id": int(phone), "amount": amount, "admin_fee": ADMIN_FEE, "total": total
        }).execute().data[0]
        
        supabase.table("transactions").insert({
            "receipt_id": receipt['id'], "user_id": int(phone), "type": "topup", "amount": total
        }).execute()
        
        supabase.table("receipts").update({"status": "approved"}).eq("id", receipt['id']).execute()
        send_wa(phone, f"Topup berhasil!\n\nNominal: Rp{amount:,}\nAdmin: Rp{ADMIN_FEE:,}\nMasuk: Rp{total:,}\n\nSaldo: Rp{user_data['balance'] + total:,}")
    else:
        send_wa(phone, "Kirim foto struk + nominal ya. Contoh: Rp50.000\n\nCek saldo: SALDO")
    
    return "ok"

if __name__ == "__main__":
    app.run()
