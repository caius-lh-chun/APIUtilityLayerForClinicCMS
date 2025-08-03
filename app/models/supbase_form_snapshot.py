from pydantic import BaseModel, Field

class FormSnapshot(BaseModel):
    ticket_id: str ##UUID
    form_id: str
    insurance_company: str
    form_name: str
    form_data: dict
    pdf_file_name: str
    version: int
    status: str ## status logic?
    ## optional created at and updated at date, ride on default create behavior?