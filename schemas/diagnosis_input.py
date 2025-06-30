from pydantic import BaseModel

class DiagnosisInput(BaseModel):
    age: float
    gender: str
    diabetes: str
    diabetes_type: str
    diarrhoea: str
    abdominal: str
    short_stature: str
    sticky_stool: str
    weight_loss: str
    iga: float
    igg: float
    igm: float
    marsh: str
    cd_type: str
