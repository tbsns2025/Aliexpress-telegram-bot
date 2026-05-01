# -*- coding: utf-8 -*-
import logging
import os
import re
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from aliexpress_utils import extract_product_id, get_product_details_by_id, generate_affiliate_link

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID', 'default')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    keyboard = [
        [InlineKeyboardButton("🛍️ كيفية الاستخدام", callback_data='how_to')],
        [InlineKeyboardButton("💰 نظام الأرباح", callback_data='earnings')],
        [InlineKeyboardButton("📞 الدعم", url='https://t.me/your_support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌟 **أهلاً بك يا {user_name} في بوت علي إكسبريس!** 🌟\n\n"
        "🚀 **ماذا يفعل هذا البوت؟**\n"
        "• يعرض لك سعر المنتج وتفاصيله\n"
        "• يحول الروابط إلى روابط عمولة\n"
        "• يساعدك على كسب المال\n\n"
        "📌 **كيف تستخدم البوت؟**\n"
        "1️⃣ أرسل رابط منتج من علي إكسبريس\n"
        "2️⃣ سأعرض لك سعر المنتج وتفاصيله\n"
        "3️⃣ سأعطيك رابط عمولة خاص بك\n"
        "4️⃣ شارك الرابط واربح عمولة\n\n"
        "💡 **نصيحة:** استخدم /help للمزيد",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **دليل استخدام البوت**\n\n"
        "🔗 **الروابط المدعومة:**\n"
        "• روابط المنتجات الطويلة\n"
        "• روابط s.click المختصرة\n\n"
        "💰 **كيف تحصل على العمولة؟**\n"
        "1. أرسل رابط منتج\n"
        "2. سأعرض لك سعر المنتج\n"
        "3. استخدم رابط العمولة\n"
        "4. كل شراء عبر رابطك = عمولة لك\n\n"
        "❓ **لديك سؤال؟**\n"
        "تواصل مع الدعم الفني",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'how_to':
        await query.edit_message_text(
            "📖 **خطوات استخدام البوت:**\n\n"
            "1️⃣ افتح علي إكسبريس\n"
            "2️⃣ اختر المنتج الذي تريده\n"
            "3️⃣ انسخ رابط المنتج\n"
            "4️⃣ أرسل الرابط إلى هذا البوت\n"
            "5️⃣ سأعرض لك سعر المنتج\n"
            "6️⃣ استخدم رابط العمولة للمشاركة\n\n"
            "✨ **هكذا ستبدأ في كسب العمولات!**",
            parse_mode='Markdown'
        )
    elif query.data == 'earnings':
        await query.edit_message_text(
            "💰 **نظام الأرباح:**\n\n"
            "• تحصل على نسبة من كل عملية شراء\n"
            "• تتبع أرباحك عبر:\n"
            "  `portals.aliexpress.com`\n\n"
            "📊 **نصائح لزيادة أرباحك:**\n"
            "• شارك المنتجات المطلوبة\n"
            "• انشر في مجموعات الشراء\n\n"
            "💪 كلما زادت مبيعاتك، زادت عمولاتك!",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # التحقق من وجود رابط
    url_pattern = re.compile(r'https?://[^\s]+')
    urls = url_pattern.findall(text)
    
    if not urls:
        await update.message.reply_text(
            "❌ **لم يتم العثور على رابط!**\n\n"
            "📌 الرجاء إرسال رابط منتج من علي إكسبريس.\n\n"
            "💡 **مثال:**\n"
            "`https://www.aliexpress.com/item/1005001234567890.html`",
            parse_mode='Markdown'
        )
        return
    
    product_url = urls[0]
    
    # التحقق من أن الرابط من علي إكسبريس
    if 'aliexpress.com' not in product_url.lower():
        await update.message.reply_text(
            "❌ **هذا الرابط ليس من علي إكسبريس!**\n\n"
            "📌 البوت يعمل فقط مع روابط AliExpress.",
            parse_mode='Markdown'
        )
        return
    
    # إرسال رسالة انتظار
    processing_msg = await update.message.reply_text("🔄 **جاري جلب معلومات المنتج...**", parse_mode='Markdown')
    
    # استخراج رقم المنتج
    product_id = extract_product_id(product_url)
    
    if not product_id:
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ **لم نتمكن من استخراج رقم المنتج من الرابط!**\n\n"
            "📌 الرجاء التأكد من الرابط والمحاولة مرة أخرى.",
            parse_mode='Markdown'
        )
        return
    
    # جلب تفاصيل المنتج
    product_name, product_image = get_product_details_by_id(product_id)
    
    # إنشاء رابط العمولة
    affiliate_link = generate_affiliate_link(product_url, TRACKING_ID)
    
    # حذف رسالة الانتظار
    await processing_msg.delete()
    
    # بناء الرسالة
    message = f"""
🏷️ **المنتج:** {product_name}

💰 **رابط العمولة الخاص بك:**
`{affiliate_link}`

✨ **كيف تستفيد؟**
• استخدم هذا الرابط للمشاركة
• كل عملية شراء عبر هذا الرابط تمنحك عمولة
• يمكنك مشاركة الرابط في أي مكان

💡 **نصيحة:** اضغط على زر نسخ الرابط ثم شاركه!
"""
    
    # أزرار المشاركة
    share_keyboard = [
        [
            InlineKeyboardButton("📋 نسخ الرابط", callback_data=f'copy_{affiliate_link}'),
            InlineKeyboardButton("📤 مشاركة", switch_inline_query=affiliate_link)
        ],
        [
            InlineKeyboardButton("💬 إرسال لصديق", url=f"https://t.me/share/url?url={affiliate_link}&text=🎁 {product_name}")
        ]
    ]
    
    # إرسال النتيجة
    try:
        if product_image:
            await update.message.reply_photo(
                photo=product_image,
                caption=message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(share_keyboard)
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(share_keyboard)
            )
    except Exception as e:
        logger.error(f"خطأ في الإرسال: {e}")
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(share_keyboard)
        )

async def copy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # استخراج الرابط من البيانات
    link = query.data.replace('copy_', '')
    await query.answer("✅ تم نسخ الرابط! يمكنك لصقه الآن في أي مكان.", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback, pattern='^(how_to|earnings)$'))
    app.add_handler(CallbackQueryHandler(copy_callback, pattern='^copy_'))
    
    logger.info('🚀 البوت يعمل بالطريقة الهجينة!')
    app.run_polling()

if __name__ == '__main__':
    main()
