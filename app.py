# -*- coding: utf-8 -*-
import logging
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    logger.error("TOKEN not found!")
    exit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 أهلاً بك في بوت علي إكسبريس!\n\n"
        "📌 أرسل لي رابط المنتج وسأقوم بتحويله.\n\n"
        "⚠️ البوت في وضع التجربة حالياً."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if 'aliexpress.com' in text.lower():
        await update.message.reply_text(
            f"✅ تم استلام الرابط!\n\n"
            f"🔗 {text}\n\n"
            f"⚠️ البوت قيد التطوير. سيتم تفعيل روابط العمولة قريباً."
        )
    else:
        await update.message.reply_text("❌ الرجاء إرسال رابط من علي إكسبريس.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("البوت يعمل...")
    app.run_polling()

if __name__ == '__main__':
    main()
