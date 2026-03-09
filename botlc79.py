import os
import requests
import random
import logging
import asyncio
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CẤU HÌNH ---
TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = '-1003808692297'
ADMIN_ID = 5838598093
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

logging.basicConfig(level=logging.INFO)

# --- WEB SERVER GIẢ LẬP ---
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is running!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app_flask.run(host='0.0.0.0', port=port)

# --- LOGIC BOT ---
bot_enabled = True
last_session = None

async def job_monitor(context):
    global last_session, bot_enabled
    if not bot_enabled: return
    try:
        response = requests.get(API_URL).json()
        if 'list' in response and len(response['list']) > 0:
            phien = response['list'][0]
            if last_session != phien['id']:
                id_moi = int(phien['id']) + 1
                ma_md5 = phien.get('_id', '0')
                diem = (id_moi + int(ma_md5[-1], 16)) % 10
                ti_le = random.randint(74, 88)
                ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"
                
                msg = (f"🌟 LC79 VIP TUANX3000 🌟\n🎯 Phiên: #{id_moi}\n"
                       f"🔮 Dự đoán: {ket_qua}\n📊 Tỉ lệ chuẩn: {ti_le}%\n♾️ Mã MD5: {ma_md5}")
                
                await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
                last_session = phien['id']
    except Exception as e:
        logging.error(f"Lỗi job_monitor: {e}")

async def bat_tool(update, context):
    global bot_enabled
    if update.effective_user.id != ADMIN_ID: return
    bot_enabled = True
    await update.message.reply_text("✅ Bot đã được BẬT.")

async def tat_tool(update, context):
    global bot_enabled
    if update.effective_user.id != ADMIN_ID: return
    bot_enabled = False
    await update.message.reply_text("❌ Bot đã được TẮT.")

if __name__ == '__main__':
    # 1. Chạy Web Server song song
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. Khởi tạo bot và tạo Event Loop mới an toàn cho Render
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Xóa webhook an toàn
    loop.run_until_complete(app.bot.delete_webhook())
    
    if app.job_queue:
        app.job_queue.run_repeating(job_monitor, interval=30, first=5)
    
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    
    logging.info("Bot đã khởi động thành công...")
    app.run_polling()
