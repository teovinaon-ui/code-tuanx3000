import os
import requests
import random
from flask import Flask
from threading import Thread
from telegram.ext import ApplicationBuilder

# --- 1. CẤU HÌNH ---
TOKEN = os.environ.get('TOKEN') # Lấy từ Environment Variables trên Render
CHANNEL_ID = '-1003808692297'
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

last_session = None

# --- 2. WEB SERVER (ĐỂ RENDER KHÔNG TẮT BOT) ---
app_web = Flask(__name__)
@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- 3. ENGINE DỰ ĐOÁN ---
async def job_monitor(context):
    global last_session
    try:
        response = requests.get(API_URL).json()
        phien = response['list'][0]
        if last_session != phien['id']:
            id_moi = int(phien['id']) + 1
            ma_md5 = phien.get('_id', '0')
            diem = (id_moi + int(ma_md5[-1], 16)) % 10
            ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"
            msg = f"🌟 LC79 VIP SYSTEM 🌟\n🎯 Phiên: #{id_moi}\n🔮 Dự đoán: {ket_qua}\n♾️ Mã MD5: {ma_md5}"
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
            last_session = phien['id']
    except Exception as e:
        print(f"Lỗi: {e}")

# --- 4. KHỞI CHẠY ---
if __name__ == '__main__':
    # Chạy Web server trong background
    Thread(target=run_web).start()
    
    # Chạy Bot Telegram
    app = ApplicationBuilder().token(TOKEN).build()
    if app.job_queue:
        app.job_queue.run_repeating(job_monitor, interval=30, first=1)
    app.run_polling()
