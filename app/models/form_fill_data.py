from pydantic import BaseModel, Field

class FormRequest(BaseModel):
    summary: str = Field(..., example="John")
    pdf_name: str = Field(..., example="Doe")