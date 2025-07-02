from fastapi import FastAPI
from services.diagnosis import diagnosis_router
from services.ingredients_scan import ingredients_router

app = FastAPI(
    title="Smart Celiac",
    description="API for Celiac Disease Diagnosis and Ingredients Scanning",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Diagnosis",
            "description": "Endpoints for Celiac disease risk prediction",
        },
        {
            "name": "Ingredients",
            "description": "Endpoints for ingredients scanning",
        },
    ]
)

app.include_router(diagnosis_router, prefix="/diagnosis", tags=["Diagnosis"])
app.include_router(ingredients_router, prefix="/scan", tags=["Ingredients"])
app.include_router(analyze_router, prefix="/analyze", tags=["Analyze"]) 

@app.get("/", include_in_schema=False)
def home():
    return {"message": "Welcome to Celiac Diagnosis API! Visit /docs for documentation."}