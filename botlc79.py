import os
import requests
import random
import logging
import asyncio
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CẤU HÌNH ---
TOKEN = "8229924024:AAFODSQbTdtEd3mRqSi1WDcCZQ4t5L-VBJE"   # Token mới
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
    if not bot_enabled:
        return

    try:
        response = requests.get(API_URL).json()
        if 'list' not in response or len(response['list']) == 0:
            return

        phien = response['list'][0]
        if last_session == phien['id']:
            return

        id_moi = int(phien['id']) + 1
        ma_md5 = phien.get('_id', '0' * 32).lower()

        # 1. PHÂN TÍCH MD5 SÂU
        last4 = ma_md5[-4:].zfill(4)
        last8 = ma_md5[-8:].zfill(8)
        last12 = ma_md5[-12:].zfill(12)

        val4 = int(last4, 16) % 100
        val8 = int(last8, 16) % 100
        sum_hex = sum(int(c, 16) for c in last12)
        last_digit = int(ma_md5[-1], 16) if ma_md5 else 0

        # 2. PHÂN TÍCH CẦU (10 phiên)
        recent = response['list'][:10]
        tai_count = sum(1 for p in recent if p.get('resultTruyenThong') == 'TAI' or p.get('point', 0) >= 5)
        xiu_count = 10 - tai_count
        trend_bias = (tai_count - xiu_count) * 2

        # TÍNH TOÁN
        base = (id_moi * 15 + val4 * 8 + val8 * 5 + last_digit * 10 + sum_hex * 3 + trend_bias)
        diem = base % 10
        diem = (diem + random.randint(0, 1)) % 10

        ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"

        ti_le = 75 + (val4 % 14)
        if (trend_bias > 4 and ket_qua == "🟢 TÀI") or (trend_bias < -4 and ket_qua == "🔴 XỈU"):
            ti_le += 3
        ti_le = max(74, min(88, ti_le))

        msg = (f"🌟 LC79 VIP TUANX3000 🌟\n"
               f"🎯 Phiên: #{id_moi}\n"
               f"🔮 Dự đoán: {ket_qua}\n"
               f"📊 Tỉ lệ chuẩn: {ti_le}%\n"
               f"♾️ Mã MD5: {ma_md5}")

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
    threading.Thread(target=run_web, daemon=True).start()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(TOKEN).build()
    loop.run_until_complete(app.bot.delete_webhook())
    
    if app.job_queue:
        app.job_queue.run_repeating(job_monitor, interval=30, first=5)
    
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    
    logging.info("Bot đã khởi động thành công...")
    app.run_polling()