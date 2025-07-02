from pydantic import BaseModel

class AnalyzeInput(BaseModel):
    barcode: str = None
    image: str = None  # Base64 encoded image
    language: str = "ar"
