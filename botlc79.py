import os
import requests
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CẤU HÌNH ---
TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = '-1003808692297'
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

bot_enabled = True
last_session = None

# --- WEB SERVER (BẮT BUỘC ĐỂ RENDER GIỮ APP CHẠY) ---
app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is running!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- HÀM TÍNH TOÁN ---
async def job_monitor(context):
    global last_session, bot_enabled
    if not bot_enabled: return
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
            print(f"Đã gửi dự đoán phiên #{id_moi}")
    except Exception as e:
        print(f"Lỗi job_monitor: {e}")

# --- COMMANDS ---
async def bat_tool(update, context):
    global bot_enabled
    bot_enabled = True
    await update.message.reply_text("✅ Đã bật.")

async def tat_tool(update, context):
    global bot_enabled
    bot_enabled = False
    await update.message.reply_text("❌ Đã tắt.")

# --- KHỞI CHẠY ---
if __name__ == '__main__':
    # 1. Chạy Web Server trong luồng phụ để không chặn bot
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # 2. Khởi tạo Telegram Bot
    if not TOKEN:
        print("Lỗi: Không tìm thấy TOKEN. Kiểm tra lại Environment Variables!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    
    # 3. Kích hoạt JobQueue
    app.job_queue.run_repeating(job_monitor, interval=30, first=5)
    
    print("Bot đã sẵn sàng và đang chạy...")
    app.run_polling()
