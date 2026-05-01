# -*- coding: utf-8 -*-
import logging
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token from environment
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🌟 أهلاً بك في بوت علي إكسبريس!\nأرسل لي رابط المنتج وسأحوله لك.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if 'aliexpress.com' in text.lower():
        await update.message.reply_text(f'✅ تم استلام الرابط: {text}\n\n⚠️ البوت في وضع الاختبار حالياً. سيتم تفعيل الروابط قريباً.')
    else:
        await update.message.reply_text('❌ الرجاء إرسال رابط منتج من علي إكسبريس.')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info('البوت يعمل...')
    app.run_polling()

if __name__ == '__main__':
    main()
