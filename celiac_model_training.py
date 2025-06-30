import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
import os

def load_data():
    df = pd.read_csv('celiac_disease_lab_data.csv')
    print("Data loaded successfully.")
    return df

def preprocess_data(df):
    df['Diabetes Type'] = df['Diabetes Type'].fillna('Type 0')
    categorical_cols = ['Gender', 'Diabetes', 'Diabetes Type', 'Diarrhoea',
                        'Abdominal', 'Short_Stature', 'Sticky_Stool',
                        'Weight_loss', 'Marsh', 'cd_type']
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
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Model accuracy: {acc:.2%}")
    return model

def save_artifacts(model, encoders):
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/celiac_model.pkl")
    joblib.dump(encoders, "models/feature_encoders.pkl")
    print("Artifacts saved successfully.")

if __name__ == "__main__":
    if not os.path.exists("celiac_disease_lab_data.csv"):
        print("Missing: celiac_disease_lab_data.csv")
        exit()
    df = load_data()
    processed_df, encoders = preprocess_data(df)
    model = train_model(processed_df)
    save_artifacts(model, encoders)
