from fastapi import APIRouter
from schemas.ingredients_input import IngredientInput

ingredients_router = APIRouter()

# كلمات تحتوي على جلوتين
gluten_keywords = [
    "wheat", "barley", "rye", "triticale", "malt", "brewer's yeast", "gluten",
    "semolina", "farina", "graham", "spelt", "kamut"
]

@ingredients_router.post("/")
def scan_ingredients(input_data: IngredientInput):
    ingredients = input_data.ingredients_text.lower()
    contains_gluten = any(keyword in ingredients for keyword in gluten_keywords)

    return {
        "contains_gluten": contains_gluten,
        "verdict": "غير آمن لمرضى السيلياك" if contains_gluten else "آمن"
    }
