# -*- coding: utf-8 -*-
import re

def extract_product_id(url):
    """استخراج رقم المنتج من الرابط"""
    if not url:
        return None
    
    # أنماط البحث عن رقم المنتج
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
    
    # إذا كان الرابط من نوع s.click
    if 's.click.aliexpress.com' in url:
        return 's_click_link'
    
    return None

def get_product_details_by_id(product_id):
    """دالة مؤقتة لجلب بيانات المنتج"""
    if not product_id:
        return None, None
    
    # اسم مؤقت للمنتج
    product_name = f"منتج رقم {product_id}"
    img_url = None
    
    return product_name, img_url
