# src/schemas/analyze_input.py
from pydantic import BaseModel
from typing import Optional

class AnalyzeInput(BaseModel):
    barcode: Optional[str] = None
    image: Optional[str] = None  # Base64 encoded image
    language: str = "ar"