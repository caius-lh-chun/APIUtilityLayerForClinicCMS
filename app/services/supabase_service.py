import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv
import supabase
import os

try:
    from dotenv import load_dotenv

    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=base_dir / ".env")  # Works locally, no error if .env missing

except ImportError:
    pass  # dotenv not installed in prod or not needed

# SUPABASE_URL = https://kkozfaofnxeehhaxwnts.supabase.co
# SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtrb3pmYW9mbnhlZWhoYXh3bnRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2ODc0OTgsImV4cCI6MjA2OTI2MzQ5OH0.X8stBlUkPT0f_LAqpKZzOPCbI8KWph3MAPyrmXeBm40
# SUPABASE_STORAGE_ID = pdf-bucket-dump


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_STORAGE_ID = os.getenv("SUPABASE_STORAGE_ID")

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)


def search_pdf_schema_by_filename(filename):
    response = (supabase_client.
                table("pdf_templates").
                select("data_schema_pdf_raw").
                eq("filename", filename).
                execute())
    return response.data[0]['data_schema_pdf_raw']

def upload_to_supabase_filled_forms(stream_bytes, uploaded_name):
        response_insert_storage = (
            supabase_client.storage
            .from_(SUPABASE_STORAGE_ID)
            .upload(
                file=stream_bytes,
                path=f"filled_pdfs/{uploaded_name}"
            )
        )
        return response_insert_storage

def update_to_supabase_filled_forms(stream_bytes, uploaded_name):
        response_insert_storage = (
            supabase_client.storage
            .from_(SUPABASE_STORAGE_ID)
            .upload(
                file=stream_bytes,
                path=f"filled_pdfs/{uploaded_name}",
                file_options={"upsert": "true"}
            )
        )
        return response_insert_storage

def download_from_supabase_storage_filled_forms(uploaded_name):
    response = (
        supabase_client.storage
        .from_(SUPABASE_STORAGE_ID)
        .download(f"filled_pdfs/{uploaded_name}")
    )
    return response

def download_from_supabase_storage_form_templates(uploaded_name):
    response = (
        supabase_client.storage
        .from_(SUPABASE_STORAGE_ID)
        .download(f"{uploaded_name}")
    )
    return response