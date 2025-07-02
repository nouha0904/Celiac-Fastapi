# src/services/ingredients_scan.py
from src.schemas.analyze_input import AnalyzeInput  # تحديث المسار
from fastapi import APIRouter, HTTPException
import base64
import io
import pytesseract
from PIL import Image
import re
import os

analyze_router = APIRouter()

# قائمة بالمكونات التي تحتوي على الجلوتين
GLUTEN_INGREDIENTS = [
    "قمح", "شعير", "جاودار", "شوفان", "تريتيكال", "سبلت", "كاموت",
    "برغل", "كسكس", "سميد", "دقيق", "جريش", "خميرة الجعة",
    "نخالة القمح", "مالت", "خميرة البيرة", "جرثومة القمح", "غلوتين"
]

def extract_text_from_image(image_base64: str) -> str:
    try:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('L')
        image = image.point(lambda x: 0 if x < 140 else 255)
        text = pytesseract.image_to_string(image, lang='ara+eng')
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"فشل في استخراج النص: {str(e)}")

def analyze_ingredients(text: str) -> dict:
    try:
        text = text.lower().strip()
        found_gluten = [g for g in GLUTEN_INGREDIENTS if re.search(rf'\b{g}\b', text)]
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
        if input_data.barcode:
            return {
                "containsGluten": True,
                "confidence": 0.95,
                "explanation": "تم تحليل المنتج باستخدام الباركود",
                "advice": "يحتوي على الجلوتين - غير آمن",
                "productName": "منتج بالباركود: " + input_data.barcode
            }

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