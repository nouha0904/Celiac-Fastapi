from fastapi import FastAPI
from services.diagnosis import diagnosis_router
from services.ingredients_scan import ingredients_router

app = FastAPI(title="Celiac API")

app.include_router(diagnosis_router, prefix="/diagnosis")
app.include_router(ingredients_router, prefix="/scan")
