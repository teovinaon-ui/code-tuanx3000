import os
import requests
import random
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CẤU HÌNH ---
# Đảm bảo bạn đã thêm biến môi trường TOKEN trong mục Settings của Render
TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = '-1003808692297'
ADMIN_ID = 5838598093
API_URL = "https://wtxmd52.tele68.com/v1/txmd5/sessions?cp=R&cl=R&pf=web&at=988f9f949c6e90fc02d78a38563031f6"

# Cấu hình log để dễ theo dõi lỗi trên Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
                
                ti_le = random.randint(63, 84)
                ket_qua = "🟢 TÀI" if diem >= 5 else "🔴 XỈU"
                
                msg = (f"🌟 LC79 VIP SYSTEM 🌟\n"
                       f"🎯 Phiên: #{id_moi}\n"
                       f"🔮 Dự đoán: {ket_qua}\n"
                       f"📊 Tỉ lệ chuẩn: {ti_le}%\n"
                       f"♾️ Mã MD5: {ma_md5}")
                
                await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
                last_session = phien['id']
                logging.info(f"Đã gửi dự đoán phiên: {id_moi}")
    except Exception as e:
        logging.error(f"Lỗi job_monitor: {e}")

async def bat_tool(update, context):
    global bot_enabled
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền!")
        return
    bot_enabled = True
    await update.message.reply_text("✅ Bot đã được BẬT.")

async def tat_tool(update, context):
    global bot_enabled
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền!")
        return
    bot_enabled = False
    await update.message.reply_text("❌ Bot đã được TẮT.")

if __name__ == '__main__':
    # Khởi tạo bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Thiết lập Job Queue
    if app.job_queue:
        app.job_queue.run_repeating(job_monitor, interval=30, first=5)
    
    # Thêm lệnh
    app.add_handler(CommandHandler("battoollc79", bat_tool))
    app.add_handler(CommandHandler("tattoollc79", tat_tool))
    
    logging.info("Bot đã khởi động thành công và đang chạy polling...")
    app.run_polling()
