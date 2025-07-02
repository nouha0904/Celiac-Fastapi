from fastapi import APIRouter, HTTPException
from schemas.diagnosis_input import DiagnosisInput
import pandas as pd
import joblib
import os
import numpy as np
from pathlib import Path

diagnosis_router = APIRouter()

# Get the absolute path to the current file
current_dir = Path(__file__).resolve().parent
MODEL_PATH = current_dir.parent / "models" / "celiac_model.pkl"
ENCODERS_PATH = current_dir.parent / "models" / "feature_encoders.pkl"

print(f"🔍 Model path: {MODEL_PATH}")
print(f"🔍 Encoders path: {ENCODERS_PATH}")

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
        # Create DataFrame from input data
        data_dict = input_data.dict()
        
        # Create a DataFrame with all expected columns
        expected_columns = [
            'Age', 'Gender', 'Diabetes', 'Diabetes Type', 'Diarrhoea', 
            'IgA', 'IgG', 'IgM', 'Abdominal', 'Short_Stature', 
            'Sticky_Stool', 'Weight_loss', 'Marsh', 'cd_type'
        ]
        
        # Initialize with zeros for all columns
        data_df = pd.DataFrame(0, index=[0], columns=expected_columns)
        
        # Map input names to expected column names
        column_mapping = {
            'age': 'Age',
            'gender': 'Gender',
            'diabetes': 'Diabetes',
            'diabetes_type': 'Diabetes Type',
            'diarrhoea': 'Diarrhoea',
            'iga': 'IgA',
            'igg': 'IgG',
            'igm': 'IgM',
            'abdominal': 'Abdominal',
            'short_stature': 'Short_Stature',
            'sticky_stool': 'Sticky_Stool',
            'weight_loss': 'Weight_loss',
            'marsh': 'Marsh',
            'cd_type': 'cd_type'
        }
        
        # Fill in values from input
        for input_name, col_name in column_mapping.items():
            if input_name in data_dict:
                data_df[col_name] = data_dict[input_name]
        
        # Encode categorical features
        categorical_cols = [
            'Gender', 'Diabetes', 'Diabetes Type', 'Diarrhoea',
            'Abdominal', 'Short_Stature', 'Sticky_Stool',
            'Weight_loss', 'Marsh', 'cd_type'
        ]
        
        for col in categorical_cols:
            if col in encoders:
                # Handle unseen categories
                all_classes = list(encoders[col].classes_)
                data_df[col] = data_df[col].apply(
                    lambda x: x if x in all_classes else all_classes[0]
                )
                data_df[col] = encoders[col].transform(data_df[col])
            else:
                print(f"⚠️ Encoder for {col} not found")
        
        # Convert to correct data types
        data_df = data_df.astype(float)
        
        # Prediction
        probability = model.predict_proba(data_df)[0]
        risk_percentage = round(probability[1] * 100, 2)
        
        # Risk assessment
        if risk_percentage > 75:
            risk_level = "High Risk"
            description = "احتمالية عالية للإصابة بمرض السيلياك. يوصى باستشارة أخصائي أمراض الجهاز الهضمي."
        elif risk_percentage > 50:
            risk_level = "Moderate Risk"
            description = "احتمالية متوسطة للإصابة. يوصى بإجراء فحوصات إضافية ومتابعة طبية."
        elif risk_percentage > 25:
            risk_level = "Low Risk"
            description = "احتمالية منخفضة للإصابة. راقب الأعراض واستشر الطبيب إذا ساءت حالتك."
        else:
            risk_level = "Very Low Risk"
            description = "احتمالية ضعيفة جدًا للإصابة. حافظ على الفحوصات الدورية."
        
        return {
            "risk_percentage": risk_percentage,
            "risk_level": risk_level,
            "description": description,
            "model_confidence": round(max(probability), 3)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"خطأ في التنبؤ: {str(e)}")