from fastapi import APIRouter,  HTTPException, Query
from fastapi.responses import FileResponse
from app.services.auto_fill_service import FormService
from app.models.form_fill_data import FormRequest
import os
from pydantic import BaseModel
from pathlib import Path

router = APIRouter()
FILLED_PDF_DIR = Path(__file__).resolve().parent.parent / "filled_pdfs"

@router.get("/")
def root():
    return {"message": "Welcome to FastAPI Boilerplate!"}


@router.post("/form-fill")
def form_fill(form_data: FormRequest):
    form_service = FormService()
    result = form_service.process_form(form_data)
    return result



class FormUpdateRequest(BaseModel):
    pdf_name: str
    field_list: list

@router.post("/update-form-fill")
def form_fill(form_data: FormUpdateRequest):
    form_service = FormService()
    result = form_service.update_form(form_data)
    return result


class DownloadRequest(BaseModel):
    filename: str

@router.post("/download-pdf")
def download_pdf(request: DownloadRequest):
    # Basic validation: only .pdf files, no path traversal
    filename = request.filename

    if not filename.endswith(".pdf") or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = FILLED_PDF_DIR / filename
    print(file_path)

    # if not file_path.is_file():
    #     raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename, media_type="application/pdf")
