import os
import requests
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CẤU HÌNH ---
TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = '-1003808692297'
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

bot_enabled = True
last_session = None

# --- HÀM TÍNH TOÁN ---
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
                ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"
                msg = f"🌟 LC79 VIP SYSTEM 🌟\n🎯 Phiên: #{id_moi}\n🔮 Dự đoán: {ket_qua}\n♾️ Mã MD5: {ma_md5}"
                await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
                last_session = phien['id']
    except Exception as e:
        print(f"Lỗi job_monitor: {e}")

async def bat_tool(update, context):
    global bot_enabled
    bot_enabled = True
    await update.message.reply_text("✅ Đã bật.")

async def tat_tool(update, context):
    global bot_enabled
    bot_enabled = False
    await update.message.reply_text("❌ Đã tắt.")

if __name__ == '__main__':
    if not TOKEN:
        print("Lỗi: Không tìm thấy TOKEN!")
        exit(1)
    
    # Khởi tạo Application kèm JobQueue
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Kiểm tra an toàn trước khi dùng JobQueue
    if app.job_queue is not None:
        app.job_queue.run_repeating(job_monitor, interval=30, first=5)
    
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    
    print("Bot đang chạy...")
    app.run_polling()
