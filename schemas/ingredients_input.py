from pydantic import BaseModel

class IngredientInput(BaseModel):
    ingredients_text: str
