import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi.responses import FileResponse,StreamingResponse
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


def search_form_snapshots_by_ticket_id(ticket_id):
    response = (supabase_client.
                table("form_snapshots").
                select("*").
                eq("ticket_id", ticket_id).
                execute())
    print(f"snapshots retrieval response {response}")
    return response.data

def insert_new_form_snapshots_for_update(formSnapshot):
    response = (supabase_client.
                table("form_snapshots").
                insert(formSnapshot.model_dump()).
                execute())
    print(f"update snapshot insertion response {response}")
    return response.data


def search_pdf_schema_by_filename(filename):
    response = (supabase_client.
                table("pdf_templates").
                select("data_schema_pdf_raw").
                eq("filename", filename).
                execute())
    print(f"schema response {response}")
    return response.data[0]['data_schema_pdf_raw']

# def upload_to_supabase_filled_forms(stream_bytes, uploaded_name):
#         response_insert_storage = (
#             supabase_client.storage
#             .from_(SUPABASE_STORAGE_ID)
#             .upload(
#                 file=stream_bytes,
#                 path=f"filled_pdfs/{uploaded_name}"
#             )
#         )
#         return response_insert_storage

# def update_to_supabase_filled_forms(stream_bytes, uploaded_name):
#         response_insert_storage = (
#             supabase_client.storage
#             .from_(SUPABASE_STORAGE_ID)
#             .upload(
#                 file=stream_bytes,
#                 path=f"filled_pdfs/{uploaded_name}",
#                 file_options={"upsert": "true"}
#             )
#         )
#         return response_insert_storage

# def download_from_supabase_storage_filled_forms(uploaded_name):
#     response = (
#         supabase_client.storage
#         .from_(SUPABASE_STORAGE_ID)
#         .download(f"filled_pdfs/{uploaded_name}")
#     )
#     return response

def download_from_supabase_storage_form_templates(uploaded_name):
    response = (
        supabase_client.storage
        .from_(SUPABASE_STORAGE_ID)
        .download(f"{uploaded_name}")
    )
    return response


def insert_filled_record_to_supabase(
    filled_filename: str,
    filled_dict: dict):
    """Insert a new PDF template."""
    data = {
        "filename": filled_filename,
        "filled_dict": json.dumps(filled_dict)
    }
    # Remove None or NaN values (if pandas is used)

    response_insert = supabase_client.table("filled_pdfs").insert(data).execute()
    return response_insert

def get_filled_record_from_supabase(
          filled_filename):
     
        response = (supabase_client.
                table("filled_pdfs").
                select("filled_dict").
                eq("filename", filled_filename).
                execute())
        
        return response.data[0]['filled_dict']

def get_latest_version_of_form_snapshots(
          ticket_id):
     
        response = (
            supabase_client.table("form_snapshots")
            .select("*")
            .eq("ticket_id", ticket_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        
        return response.data[0]



def update_filled_record(
    filled_filename: str,
    filled_dict: dict):
    """Insert a new PDF template."""
    data = {
        "filename": filled_filename,
        "filled_dict": json.dumps(filled_dict)
    }
    # Remove None or NaN values (if pandas is used)

    response_update = (supabase_client.table("filled_pdfs")
                       .update({"filled_dict":filled_dict})
                       .eq("filename",filled_filename)
                       .execute())
    return response_update


# .update({"name": "piano"})    .eq("id", 1)    .execute())