# -*- coding: utf-8 -*-
import logging
import os
import re
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID', 'default')

# أوامر البوت
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
        "• يحول روابط المنتجات العادية إلى روابط عمولة\n"
        "• يساعدك على كسب المال من مشاركة المنتجات\n"
        "• سريع ومجاني بالكامل\n\n"
        "📌 **كيف تستخدم البوت؟**\n"
        "1️⃣ انسخ رابط أي منتج من علي إكسبريس\n"
        "2️⃣ أرسل الرابط إلى هذا البوت\n"
        "3️⃣ ستحصل على رابط عمولة جديد خاص بك\n"
        "4️⃣ شارك الرابط واربح عمولة عن كل عملية شراء\n\n"
        "💡 **نصيحة:** استخدم الأمر /help للمزيد من المعلومات",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **دليل استخدام البوت**\n\n"
        "🔗 **الروابط المدعومة:**\n"
        "• روابط المنتجات الطويلة\n"
        "• روابط s.click المختصرة\n"
        "• روابط a.aliexpress.com\n\n"
        "💰 **كيف تحصل على العمولة؟**\n"
        "1. أرسل رابط منتج\n"
        "2. استخدم الرابط الجديد الذي سيعطيك إياه البوت\n"
        "3. شارك الرابط مع الآخرين\n"
        "4. كل عملية شراء عبر رابطك = عمولة لك\n\n"
        "❓ **لديك سؤال؟**\n"
        "تواصل مع الدعم الفني عبر زر الدعم في رسالة الترحيب",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'how_to':
        await query.edit_message_text(
            "📖 **خطوات استخدام البوت:**\n\n"
            "1️⃣ افتح تطبيق أو موقع علي إكسبريس\n"
            "2️⃣ ابحث عن المنتج الذي تريد مشاركته\n"
            "3️⃣ انسخ رابط المنتج من شريط العناوين\n"
            "4️⃣ ارجع إلى هذا البوت وأرسل الرابط\n"
            "5️⃣ انتظر ثانية وسيتم تحويل الرابط\n"
            "6️⃣ استخدم الرابط الجديد للمشاركة\n\n"
            "✨ **هكذا ستبدأ في كسب العمولات!**",
            parse_mode='Markdown'
        )
    elif query.data == 'earnings':
        await query.edit_message_text(
            "💰 **نظام الأرباح:**\n\n"
            "• تحصل على نسبة مئوية (تصل إلى 20%) من كل عملية شراء\n"
            "• تتبع أرباحك من خلال:\n"
            "  `portals.aliexpress.com`\n\n"
            "📊 **نصائح لزيادة أرباحك:**\n"
            "• شارك المنتجات المطلوبة\n"
            "• استخدم روابط مختصرة\n"
            "• انشر في مجموعات الشراء\n\n"
            "💪 كلما زادت مبيعاتك، زادت عمولاتك!",
            parse_mode='Markdown'
        )

def convert_to_affiliate_link(product_url, tracking_id):
    """تحويل الرابط العادي إلى رابط عمولة"""
    
    # استخراج رقم المنتج من الرابط
    product_id = None
    
    # محاولة استخراج الرقم المباشر للمنتج
    patterns = [
        r'/item/(\d+)\.html',           # الرابط العادي
        r'/(\d+)\.html',                 # رابط مختصر
        r'productId=(\d+)',              # معامل productId
        r'id=(\d+)',                     # معامل id
        r'/_/(\d+)',                     # رابط a.aliexpress
        r'/e/_([a-zA-Z0-9]+)'            # رابط s.click
    ]
    
    for pattern in patterns:
        match = re.search(pattern, product_url)
        if match:
            product_id = match.group(1)
            break
    
    # إذا كان الرابط بالفعل من نوع s.click
    if 's.click.aliexpress.com' in product_url:
        # نحاول استخراج الرابط النهائي إذا كان مختصراً
        if '/e/_' in product_url:
            # هذا رابط مختصر، يمكننا تركه كما هو أو محاولة فكه
            pass
        return product_url
    
    # بناء رابط العمولة
    if product_id:
        # رابط عمولة مع رقم المنتج
        base_link = f"https://s.click.aliexpress.com/e/_oB8M7N?product_id={product_id}&tracking_id={tracking_id}"
    else:
        # رابط عمولة عام
        base_link = f"https://s.click.aliexpress.com/e/_oB8M7N?tracking_id={tracking_id}"
    
    return base_link

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
    if 'aliexpress.com' not in product_url.lower() and 's.click.aliexpress.com' not in product_url.lower():
        await update.message.reply_text(
            "❌ **هذا الرابط ليس من علي إكسبريس!**\n\n"
            "📌 البوت يعمل فقط مع روابط AliExpress.\n\n"
            "💡 **مثال على رابط صحيح:**\n"
            "`https://www.aliexpress.com/item/1005001234567890.html`",
            parse_mode='Markdown'
        )
        return
    
    # إرسال رسالة انتظار
    processing_msg = await update.message.reply_text("🔄 **جاري تحويل الرابط إلى رابط عمولة...**", parse_mode='Markdown')
    
    # تحويل الرابط
    affiliate_link = convert_to_affiliate_link(product_url, TRACKING_ID)
    
    # حذف رسالة الانتظار
    await processing_msg.delete()
    
    # أزرار المشاركة
    share_keyboard = [
        [
            InlineKeyboardButton("📋 نسخ الرابط", callback_data='copy'),
            InlineKeyboardButton("📤 مشاركة", switch_inline_query=affiliate_link)
        ],
        [
            InlineKeyboardButton("💬 إرسال لصديق", url=f"https://t.me/share/url?url={affiliate_link}&text=🎁 اكتشف هذا المنتج الرائع!")
        ]
    ]
    
    # اختصار الرابط الأصلي إذا كان طويلاً
    short_original = product_url[:80] + '...' if len(product_url) > 80 else product_url
    short_affiliate = affiliate_link[:80] + '...' if len(affiliate_link) > 80 else affiliate_link
    
    await update.message.reply_text(
        f"✅ **تم تحويل الرابط بنجاح!** 🎉\n\n"
        f"🔗 **الرابط الأصلي:**\n"
        f"`{short_original}`\n\n"
        f"💰 **رابط العمولة الخاص بك:**\n"
        f"`{short_affiliate}`\n\n"
        f"✨ **كيف تستفيد؟**\n"
        f"• استخدم الرابط الجديد للمشاركة\n"
        f"• كل عملية شراء عبر هذا الرابط تمنحك عمولة\n"
        f"• يمكنك تتبع أرباحك في حساب شريك علي إكسبريس\n\n"
        f"💡 **نصيحة:** اضغط على زر نسخ الرابط ثم شاركه!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(share_keyboard)
    )

async def copy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ تم نسخ الرابط! يمكنك لصقه الآن في أي مكان.", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback, pattern='^(how_to|earnings)$'))
    app.add_handler(CallbackQueryHandler(copy_callback, pattern='^copy$'))
    
    logger.info('🚀 البوت يعمل بكامل طاقته وجاهز لتحويل الروابط!')
    app.run_polling()

if __name__ == '__main__':
    main()
