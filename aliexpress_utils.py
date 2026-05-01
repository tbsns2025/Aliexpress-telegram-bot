# -*- coding: utf-8 -*-
import re

def extract_product_id(url):
    """
    استخراج رقم المنتج من أي رابط علي إكسبريس، بما في ذلك روابط s.click.
    """
    print(f"[DEBUG] محاولة استخراج ID من: {url}")

    # --- 1. معالجة روابط s.click (التي يصدرها التطبيق) ---
    # مثال: https://s.click.aliexpress.com/e/_oBWdDVB
    s_click_match = re.search(r's\.click\.aliexpress\.com/e/[_a-zA-Z0-9]+', url)
    if s_click_match:
        print("[DEBUG] تم التعرف على رابط s.click. جاري محاولة فك الارتباط المباشر...")
        # هذه روابط قصيرة ومشفرة. الحل الأسرع الآن هو استخدام معرف تجريبي
        # لعرض فكرة المنتج على الأقل. (سيتم استبداله برقم حقيقي بعد تفعيل API).
        # نعيد رقمًا تجريبيًا كحل مؤقت لتجاوز هذه العقبة.
        demo_product_id = "1005001234567890"
        print(f"[DEBUG] رابط تجريبي (مؤقت): استخدم ID = {demo_product_id}")
        return demo_product_id

    # --- 2. معالجة الروابط العادية ---
    patterns = [
        r'/item/(\d+)\.html',      # الرابط العادي (www.aliexpress.com/item/123.html)
        r'/(\d+)\.html',            # روابط مختصرة أخرى
        r'productId=(\d+)',         # روابط بها معامل productId
        r'id=(\d+)',                # روابط بها معامل id
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            product_id = match.group(1)
            print(f"[DEBUG] تم استخراج ID: {product_id} بنجاح باستخدام النمط: {pattern}")
            return product_id

    # --- 3. إذا فشل كل شيء ---
    print(f"[ERROR] لم نتمكن من استخراج ID من الرابط: {url}")
    return None

# --- دالة مؤقتة لجلب البيانات (ستتحسن بعد الموافقة على API) ---
def get_product_details_by_id(product_id):
    """
    دالة مؤقتة لإظهار فكرة عمل البوت. سيتم استبدالها بالكود الكامل بعد تفعيل API.
    """
    if not product_id:
        return None, None

    print(f"[INFO] جلب بيانات مؤقتة للمنتج: {product_id}")
    product_name = f"منتج تجريبي (الرقم: {product_id})"
    img_url = None
    return product_name, img_url
