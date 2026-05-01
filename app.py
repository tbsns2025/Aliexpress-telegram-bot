# -*- coding: utf-8 -*-
import logging
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ALIEXPRESS_TRACKING_ID = os.getenv('ALIEXPRESS_TRACKING_ID', 'default')

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    # إنشاء أزرار تفاعلية
    keyboard = [
        [
            InlineKeyboardButton("🛍️ كيفية الاستخدام", callback_data='how_to_use'),
            InlineKeyboardButton("💰 أرباحي", callback_data='my_earnings')
        ],
        [
            InlineKeyboardButton("📞 الدعم", url='https://t.me/your_support'),
            InlineKeyboardButton("⭐ تقييم البوت", url='https://t.me/your_channel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🌟 **أهلاً بك يا {user_name} في بوت علي إكسبريس المطور!** 🌟

✨ **ماذا يميز هذا البوت؟**
• يحول أي رابط منتج إلى رابط عمولة تلقائياً
• يساعدك على كسب المال من مشاركة الروابط
• سريع ومجاني 24 ساعة

📌 **كيف تستخدم البوت؟**
1️⃣ اذهب إلى موقع علي إكسبريس
2️⃣ انسخ رابط المنتج الذي تريد مشاركته
3️⃣ أرسل الرابط هنا
4️⃣ ستحصل على رابط عمولة جاهز للمشاركة

💰 **ملاحظة:** كل عملية شراء عبر رابطك تمنحك عمولة!
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **دليل استخدام البوت**

1️⃣ **إرسال رابط:** أرسل أي رابط منتج من علي إكسبريس
2️⃣ **الحصول على رابط عمولة:** سيرد البوت برابط جديد مخصص لك
3️⃣ **مشاركة الرابط:** شارك الرابط مع أصدقائك أو على وسائل التواصل
4️⃣ **كسب العمولات:** كل عملية شراء عبر رابطك تمنحك نسبة مئوية

🔗 **أمثلة على الروابط المقبولة:**
• `https://www.aliexpress.com/item/1005001234567890.html`
• `https://s.click.aliexpress.com/e/_xxxxx`

💡 **نصيحة:** الروابط المختصرة تعمل أيضاً!

❓ **لديك سؤال؟** تواصل مع الدعم عبر الزر الموجود في رسالة الترحيب.
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'how_to_use':
        await query.edit_message_text(
            "📖 **كيفية استخدام البوت خطوة بخطوة:**\n\n"
            "1. ابحث عن منتج على AliExpress\n"
            "2. انسخ رابط المنتج\n"
            "3. أرسل الرابط إلى هذا البوت\n"
            "4. استخدم الرابط الجديد الذي سيعطيك إياه البوت\n"
            "5. شارك الرابط مع الآخرين\n\n"
            "💰 كل عملية شراء عبر رابطك = عمولة لك!",
            parse_mode='Markdown'
        )
    elif query.data == 'my_earnings':
        await query.edit_message_text(
            "💰 **نظام الأرباح:**\n\n"
            "• تحصل على نسبة مئوية من كل عملية شراء تتم عبر رابطك\n"
            "• النسبة تختلف حسب نوع المنتج والعرض\n"
            "• يمكنك متابعة أرباحك من خلال حسابك في برنامج شركاء علي إكسبريس\n\n"
            "🔗 سجل دخول إلى: `portals.aliexpress.com` لمشاهدة أرباحك",
            parse_mode='Markdown'
        )

def generate_affiliate_link(original_url, tracking_id):
    """Convert regular AliExpress link to affiliate link"""
    try:
        # إذا كان الرابط بالفعل رابط عمولة، أعد نفس الرابط
        if 's.click.aliexpress.com' in original_url:
            return original_url
        
        # استخراج رقم المنتج من الرابط إن أمكن
        product_id_match = re.search(r'/item/(\d+)\.html', original_url)
        if product_id_match:
            product_id = product_id_match.group(1)
            # رابط عمولة مباشر (مبسط)
            return f"https://s.click.aliexpress.com/e/_oB8M7N?product_id={product_id}&tracking_id={tracking_id}"
        
        # رابط عمولة عام
        return f"https://s.click.aliexpress.com/e/_oB8M7N?tracking_id={tracking_id}"
        
    except Exception as e:
        logger.error(f"Error generating affiliate link: {e}")
        return original_url

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # التحقق من وجود رابط علي إكسبريس
    if 'aliexpress.com' in text.lower() or 's.click.aliexpress.com' in text.lower():
        
        # إرسال رسالة انتظار
        processing_msg = await update.message.reply_text("🔄 **جاري تحويل الرابط إلى رابط عمولة...**", parse_mode='Markdown')
        
        # إنشاء رابط العمولة
        affiliate_link = generate_affiliate_link(text, ALIEXPRESS_TRACKING_ID)
        
        # حذف رسالة الانتظار
        await processing_msg.delete()
        
        # إنشاء أزرار للمشاركة السريعة
        share_keyboard = [
            [
                InlineKeyboardButton("📱 مشاركة على تلغرام", switch_inline_query=affiliate_link),
                InlineKeyboardButton("💬 مشاركة مع صديق", url=f"https://t.me/share/url?url={affiliate_link}&text=🎁 اكتشف هذا المنتج الرائع!")
            ],
            [
                InlineKeyboardButton("🔗 نسخ الرابط", callback_data='copy_link'),
                InlineKeyboardButton("📊 شرح الأرباح", callback_data='my_earnings')
            ]
        ]
        share_markup = InlineKeyboardMarkup(share_keyboard)
        
        # إرسال النتيجة النهائية
        result_message = f"""
✅ **تم تحويل الرابط بنجاح!**

🔗 **الرابط الأصلي:**
<code>{text[:100]}{'...' if len(text) > 100 else ''}</code>

💰 **رابط العمولة الخاص بك:**
<code>{affiliate_link}</code>

✨ **ملاحظة مهمة:**
• كل عملية شراء عبر هذا الرابط تمنحك عمولة
• يمكنك مشاركة هذا الرابط في أي مكان
• لا تنسى استخدام الروابط المختصرة لتسهيل النشر

💡 **نصيحة:** اضغط على زر "نسخ الرابط" ثم شاركه مع أصدقائك!
"""
        await update.message.reply_text(result_message, parse_mode='HTML', reply_markup=share_markup)
        
    else:
        await update.message.reply_text(
            "❌ **عذراً، لم نتعرف على رابط علي إكسبريس!**\n\n"
            "📌 الرجاء إرسال رابط منتج صالح، مثل:\n"
            "<code>https://www.aliexpress.com/item/1005001234567890.html</code>\n\n"
            "🛍️ يمكنك الحصول على الرابط من تطبيق أو موقع علي إكسبريس.",
            parse_mode='HTML'
        )

def main():
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # معالج الأزرار التفاعلية
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info('🚀 البوت المطور يعمل بكامل طاقته!')
    app.run_polling()

if __name__ == '__main__':
    main()
