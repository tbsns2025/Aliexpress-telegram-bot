# -*- coding: utf-8 -*-
import logging
import os
import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALIEXPRESS_TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID', 'default')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🌟 أهلاً بك في بوت علي إكسبريس! 🌟\n\n'
        '📌 أرسل لي رابط المنتج وسأقوم بتحويله إلى رابط عمولة.\n\n'
        '💰当عند الشراء عبر الرابط الجديد، ستحصل على أفضل سعر وتدعم تطوير البوت.'
    )

def generate_affiliate_link(original_url, tracking_id):
    """Convert regular AliExpress link to affiliate link"""
    try:
        # This is a simple conversion - replace with actual API call later
        if 'aliexpress.com' in original_url:
            # Check if it's already an affiliate link
            if 's.click.aliexpress.com' in original_url:
                return original_url
            # Simple conversion for now
            return f"https://s.click.aliexpress.com/e/_oB8M7N?tracking_id={tracking_id}"
        return original_url
    except Exception as e:
        logger.error(f"Error generating affiliate link: {e}")
        return original_url

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if 'aliexpress.com' in text.lower() or 's.click.aliexpress.com' in text.lower():
        await update.message.reply_text('🔄 جاري تحويل الرابط إلى رابط عمولة...')
        
        # Generate affiliate link
        affiliate_link = generate_affiliate_link(text, ALIEXPRESS_TRACKING_ID)
        
        # Send response
        response = f"""
🔗 <b>الرابط الأصلي:</b>
<code>{text}</code>

💰 <b>رابط العمولة (للكسب من الشراء):</b>
<code>{affiliate_link}</code>

💡 <b>ملاحظة:</b> عند الشراء عبر رابط العمولة، تحصل على أفضل الأسعار وتدعم تطوير البوت!
"""
        await update.message.reply_text(response, parse_mode='HTML')
    else:
        await update.message.reply_text(
            '❌ الرجاء إرسال رابط منتج من علي إكسبريس.\n\n'
            'مثال: https://www.aliexpress.com/item/1234567890.html'
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info('🚀 البوت يعمل ويحول الروابط إلى روابط عمولة!')
    app.run_polling()

if __name__ == '__main__':
    main()
