import re
import requests
from bs4 import BeautifulSoup

def extract_product_id(url):
    """استخراج رقم المنتج من الرابط"""
    patterns = [
        r'/item/(\d+)\.html',
        r'/(\d+)\.html',
        r'productId=(\d+)',
        r'id=(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_product_details_by_id(product_id):
    """
    جلب تفاصيل المنتج - طريقة هجينة
    تحاول أولاً عبر API، ثم عبر scraping مباشرة
    """
    print(f"جلب تفاصيل المنتج: {product_id}")
    
    # بناء رابط المنتج
    product_url = f"https://www.aliexpress.com/item/{product_id}.html"
    print(f"رابط المنتج: {product_url}")
    
    # محاولة جلب البيانات عبر scraping مباشر
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(product_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # محاولة استخراج الاسم
            title_tag = soup.find('title')
            product_name = title_tag.text.strip() if title_tag else f"Product {product_id}"
            # تنظيف الاسم
            product_name = product_name.split('|')[0].strip() if '|' in product_name else product_name
            product_name = product_name.split('-')[0].strip() if '-' in product_name else product_name
            
            # رابط الصورة (افتراضي)
            img_url = None
            
            print(f"تم جلب المنتج بنجاح: {product_name}")
            return product_name, img_url
        else:
            print(f"فشل جلب الصفحة: {response.status_code}")
            return f"Product {product_id}", None
            
    except Exception as e:
        print(f"خطأ في جلب المنتج: {e}")
        return f"Product {product_id}", None

# دالة إضافية لإنشاء روابط العمولة
def generate_affiliate_link(product_url, tracking_id):
    """إنشاء رابط عمولة من رابط عادي"""
    product_id = extract_product_id(product_url)
    if product_id:
        # رابط عمولة تجريبي (سيتحول إلى رابط حقيقي بعد تفعيل API)
        return f"https://s.click.aliexpress.com/e/_oB8M7N?product_id={product_id}&tracking_id={tracking_id}"
    return product_url
