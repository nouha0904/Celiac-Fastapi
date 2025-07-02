from fastapi import APIRouter, HTTPException
from schemas.diagnosis_input import DiagnosisInput
import pandas as pd
import joblib
import os
import numpy as np

diagnosis_router = APIRouter()

# حل مشكلة تحميل النموذج
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "../../models/celiac_model.pkl")
ENCODERS_PATH = os.path.join(MODEL_DIR, "../../models/feature_encoders.pkl")

try:
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    print("✅ Model and encoders loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    encoders = None

@diagnosis_router.post("/")
def diagnose(input_data: DiagnosisInput):
    if model is None or encoders is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Please check server logs.")
    
    try:
        # إنشاء DataFrame من بيانات الإدخال
        data_dict = input_data.dict()
        data_df = pd.DataFrame([data_dict])
        
        # ترميز البيانات الفئوية
        categorical_cols = [
            'Gender', 'Diabetes', 'Diabetes Type', 'Diarrhoea',
            'Abdominal', 'Short_Stature', 'Sticky_Stool',
            'Weight_loss', 'Marsh', 'cd_type'
        ]
        
        # تعيين الأسماء الصحيحة للأعمدة
        column_mapping = {
            'gender': 'Gender',
            'diabetes': 'Diabetes',
            'diabetes_type': 'Diabetes Type',
            'diarrhoea': 'Diarrhoea',
            'abdominal': 'Abdominal',
            'short_stature': 'Short_Stature',
            'sticky_stool': 'Sticky_Stool',
            'weight_loss': 'Weight_loss',
            'marsh': 'Marsh',
            'cd_type': 'cd_type'
        }
        
        data_df.rename(columns=column_mapping, inplace=True)
        
        # تطبيق الترميز على كل عمود
        for col in categorical_cols:
            if col in data_df.columns:
                # معالجة القيم الجديدة
                all_classes = list(encoders[col].classes_)
                data_df[col] = data_df[col].apply(
                    lambda x: x if x in all_classes else all_classes[0]
                )
                data_df[col] = encoders[col].transform(data_df[col])
        
        # إعادة ترتيب الأعمدة كما في بيانات التدريب
        expected_columns = [
            'Age', 'Gender', 'Diabetes', 'Diabetes Type', 'Diarrhoea', 'IgA', 'IgG', 'IgM',
            'Abdominal', 'Short_Stature', 'Sticky_Stool', 'Weight_loss', 'Marsh', 'cd_type'
        ]
        
        # إضافة أي أعمدة مفقودة بقيمة صفر
        for col in expected_columns:
            if col not in data_df.columns:
                data_df[col] = 0
        
        data_df = data_df[expected_columns]
        
        # التنبؤ
        probability = model.predict_proba(data_df)[0]
        risk_percentage = round(probability[1] * 100, 2)
        
        # تحديد مستوى الخطورة
        if risk_percentage > 75:
            risk_level = "High Risk"
            description = "Strong likelihood of Celiac disease. Consultation with a gastroenterologist is highly recommended."
        elif risk_percentage > 50:
            risk_level = "Moderate Risk"
            description = "Possible Celiac disease. Further testing and medical consultation advised."
        elif risk_percentage > 25:
            risk_level = "Low Risk"
            description = "Low probability of Celiac disease. Monitor symptoms and consult if conditions worsen."
        else:
            risk_level = "Very Low Risk"
            description = "Unlikely to have Celiac disease. Maintain regular checkups."
        
        return {
            "risk_percentage": risk_percentage,
            "risk_level": risk_level,
            "description": description,
            "model_confidence": round(max(probability), 3)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")