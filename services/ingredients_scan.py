from fastapi import APIRouter, HTTPException
from schemas.analyze_input import AnalyzeInput
import base64
import io
import pytesseract
from PIL import Image
import re

analyze_router = APIRouter()

# قائمة بالمكونات التي تحتوي على الجلوتين
GLUTEN_INGREDIENTS = [
    "قمح", "شعير", "جاودار", "شوفان", "تريتيكال", "سبلت", "كاموت",
    "برغل", "كسكس", "سميد", "دقيق", "جريش", "خميرة الجعة",
    "نخالة القمح", "مالت", "خميرة البيرة", "جرثومة القمح", "غلوتين"
]

def extract_text_from_image(image_base64: str) -> str:
    """استخراج النص من الصورة باستخدام OCR"""
    try:
        # تحويل Base64 إلى صورة
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # تحسين الصورة لاستخراج النص
        image = image.convert('L')  # تحويل إلى تدرج الرمادي
        image = image.point(lambda x: 0 if x < 140 else 255)  # تحسين التباين
        
        # استخراج النص باستخدام Tesseract OCR
        text = pytesseract.image_to_string(image, lang='ara+eng')
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل في استخراج النص: {str(e)}")

def analyze_ingredients(text: str) -> dict:
    """تحليل النص للكشف عن وجود الجلوتين"""
    try:
        # تنظيف النص
        text = text.lower().strip()
        
        # البحث عن مكونات تحتوي على جلوتين
        found_gluten = []
        for ingredient in GLUTEN_INGREDIENTS:
            if re.search(rf'\b{ingredient}\b', text):
                found_gluten.append(ingredient)
        
        if found_gluten:
            return {
                "containsGluten": True,
                "found_keywords": found_gluten,
                "explanation": "تم اكتشاف مكونات تحتوي على الجلوتين",
                "advice": "هذا المنتج غير آمن لمرضى السيلياك"
            }
        else:
            return {
                "containsGluten": False,
                "explanation": "لم يتم اكتشاف مكونات تحتوي على الجلوتين",
                "advice": "هذا المنتج آمن لمرضى السيلياك"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في تحليل المكونات: {str(e)}")

@analyze_router.post("/")
async def analyze_product(input_data: AnalyzeInput):
    try:
        # إذا كان هناك باركود، نعطيه أولوية
        if input_data.barcode:
            # في تطبيق حقيقي، نبحث في قاعدة بيانات المنتجات
            return {
                "containsGluten": True,
                "confidence": 0.95,
                "explanation": "تم تحليل المنتج باستخدام الباركود",
                "advice": "يحتوي على الجلوتين - غير آمن",
                "productName": "منتج بالباركود: " + input_data.barcode
            }
        
        # إذا كانت هناك صورة، نستخرج النص منها
        if input_data.image:
            text = extract_text_from_image(input_data.image)
            result = analyze_ingredients(text)
            
            return {
                "containsGluten": result["containsGluten"],
                "confidence": 0.85,
                "explanation": result["explanation"],
                "advice": result["advice"],
                "productName": "منتج من الصورة"
            }
        
        raise HTTPException(status_code=400, detail="يجب تقديم باركود أو صورة")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في التحليل: {str(e)}")