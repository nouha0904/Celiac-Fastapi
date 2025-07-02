import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def load_data():
    # بيانات نموذجية للتدريب
    data = {
        'Age': [25, 30, 45, 35, 28, 50, 32, 22, 40, 55, 29, 33, 48],
        'Gender': ['male', 'female', 'female', 'male', 'male', 'female', 'male', 'female', 'male', 'female', 'male', 'female', 'male'],
        'Diabetes': ['no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'yes'],
        'Diabetes Type': ['none', 'type1', 'none', 'type2', 'none', 'type2', 'none', 'none', 'type1', 'none', 'type2', 'none', 'type1'],
        'Diarrhoea': ['none', 'watery', 'fatty', 'watery', 'none', 'fatty', 'none', 'watery', 'fatty', 'none', 'watery', 'fatty', 'none'],
        'IgA': [120, 85, 150, 90, 110, 95, 130, 140, 80, 160, 100, 115, 125],
        'IgG': [900, 1200, 800, 1100, 950, 1300, 1000, 850, 1400, 750, 920, 1050, 980],
        'IgM': [80, 120, 70, 100, 90, 110, 85, 75, 130, 65, 95, 82, 88],
        'Abdominal': ['yes', 'yes', 'no', 'yes', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes'],
        'Short_Stature': ['PSS', 'NSS', 'PSS', 'NSS', 'PSS', 'NSS', 'PSS', 'NSS', 'PSS', 'NSS', 'PSS', 'NSS', 'PSS'],
        'Sticky_Stool': ['yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes'],
        'Weight_loss': ['yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes'],
        'Marsh': ['type 0', 'type 1', 'type 3', 'type 2', 'type 0', 'type 3', 'type 1', 'type 0', 'type 3', 'type 2', 'type 1', 'type 2', 'type 3'],
        'cd_type': ['typical', 'atypical', 'silent', 'typical', 'atypical', 'silent', 'typical', 'atypical', 'silent', 'typical', 'atypical', 'silent', 'typical'],
        'Disease_Diagnose': ['no', 'yes', 'yes', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'yes', 'yes', 'yes', 'no']
    }
    df = pd.DataFrame(data)
    print("✅ Sample data created successfully!")
    return df

def preprocess_data(df):
    df['Diabetes Type'] = df['Diabetes Type'].fillna('none')
    categorical_cols = [
        'Gender', 'Diabetes', 'Diabetes Type', 'Diarrhoea',
        'Abdominal', 'Short_Stature', 'Sticky_Stool',
        'Weight_loss', 'Marsh', 'cd_type'
    ]
    
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
    
    df = df.drop_duplicates()
    return df, encoders

def train_model(df):
    X = df.drop('Disease_Diagnose', axis=1)
    y = df['Disease_Diagnose'].map({'yes': 1, 'no': 0})
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # تقييم النموذج
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {acc:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return model

def save_artifacts(model, encoders):
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/celiac_model.pkl")
    joblib.dump(encoders, "models/feature_encoders.pkl")
    print("✅ Artifacts saved successfully!")

if __name__ == "__main__":
    print("Starting model training...")
    df = load_data()
    processed_df, encoders = preprocess_data(df)
    model = train_model(processed_df)
    save_artifacts(model, encoders)
    print("Model training completed!")