from fastapi import APIRouter, HTTPException
from schemas.diagnosis_input import DiagnosisInput
import pandas as pd
import joblib
import os

diagnosis_router = APIRouter()

# تحميل النموذج والمشفرات
try:
    model_path = os.path.join(os.path.dirname(__file__), "../models/celiac_model.pkl")
    enc_path = os.path.join(os.path.dirname(__file__), "../models/feature_encoders.pkl")

    model = joblib.load(model_path)
    encoders = joblib.load(enc_path)
except Exception as e:
    print("❌ Error loading model or encoders:", e)
    model = None
    encoders = None

@diagnosis_router.post("/")
def diagnose(input_data: DiagnosisInput):
    # تحقق من وجود النموذج والمشفرات
    if model is None or encoders is None:
        raise HTTPException(status_code=500, detail="Model or encoders not loaded.")

    try:
        # تجهيز البيانات
        data = pd.DataFrame([input_data.dict()])

        # ترميز البيانات الفئوية
        for col, encoder in encoders.items():
            data[col] = encoder.transform(data[col])

        # توقع
        probability = model.predict_proba(data)[0][1]
        risk_percentage = round(probability * 100, 2)

        # تصنيف الخطورة
        if risk_percentage > 75:
            risk_level = "خطورة عالية"
            desc = "هناك احتمالية كبيرة للإصابة."
        elif risk_percentage > 40:
            risk_level = "خطورة متوسطة"
            desc = "مراقبة الأعراض مطلوبة."
        else:
            risk_level = "خطورة منخفضة"
            desc = "الوضع مستقر."

        return {
            "risk_percentage": risk_percentage,
            "risk_level": risk_level,
            "description": desc
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
