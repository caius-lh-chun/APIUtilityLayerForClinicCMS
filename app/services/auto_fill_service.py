import pandas as pd
import json
from app.models.form_fill_data import FormRequest
from pathlib import Path
from google import genai
from datetime import datetime
from dotenv import load_dotenv
import time
import fitz
import os

try:
    from dotenv import load_dotenv

    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=base_dir / ".env")  # Works locally, no error if .env missing
except ImportError:
    pass  # dotenv not installed in prod or not needed

class FormService:


    csv_path = base_dir / "data_schema_20250716_182641.csv"
    pdf_template_dir = base_dir / "pdf_templates"
    filled_in_pdf_template_dir = base_dir / "filled_pdfs"

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)


    def __init__(self):
        # Initialize service dependencies here (e.g., DB, external APIs)
        pass


    def update_form(self, update_dto):

        required_object = {
            "filled_pdf_file_name": None,
            # "filled_pdf_dict_raw": None
        }

        filename = update_dto.pdf_name
        list_for_update_widget = update_dto.field_list

        saved_file_name = self.update_pdf_fields(list_for_update_widget, filename)

        required_object['filled_pdf_file_name'] = saved_file_name

        return required_object


    def process_form(self, form_data: FormRequest) -> dict:

        required_object = {
            "filled_pdf_file_name": None,
            "predefined_json": None,
            "filled_pdf_dict_raw": None
        }


        # Business logic goes here.
        # For example, validate, save to DB, send email, etc.

        # Dummy implementation:
        # full_name = f"{form_data.first_name} {form_data.last_name}"

        filename = form_data.pdf_name
        print(f"processing {filename}")
        summary = form_data.summary
        print(f"received summary {summary}")

    #     demo purpose: valid file names
    #     array(['AIA hospital OPCLMF03.pdf.coredownload.inline.pdf',
    #    'AXA hospitalization Claim Form -GE_HK_Fillable.pdf',
    #    'Prudential hospital claim form.pdf'], dtype=object)


        pdf_schema = self.get_schema(filenamepdf=f'{filename}')
        print(f"retried schema")

        ## after get schema, fill in PDF and save somewhere and return defined fields from here

        filled_in_dict = {}

        for page, widget in pdf_schema.items():
            prompt_for_task = self.fill_fields_prompt(widget,summary)
            result = self.invoking_gemini(path_to_image=None, prompt=prompt_for_task)
            filled_in_dict[page] = result

        ## after load json, add id for each element

        print(filled_in_dict[page])

        return_dict = {
            "field_list" : []
        }

        for page, pageJsonList in filled_in_dict.items():
            
            pageJsonList = json.loads(pageJsonList)
            pageJsonDict = {e['xref']: e for e in pageJsonList}

            for x in pdf_schema[page]:
                toFillXref = x['xref']
                newObject = {
                    'id': f"{toFillXref}_{x['name']}",
                    'value': None  # default
                }
                
                if toFillXref in pageJsonDict:
                    newObject['value'] = pageJsonDict[toFillXref].get('value')
                
                return_dict["field_list"].append(newObject)
            
        

        print(f"retrieved filled dict JSON")

        saved_file_name = self.fill_pdf_fields(filled_in_dict=filled_in_dict,filename=filename)

        print(f"saved PDF as {saved_file_name}")


        required_object['filled_pdf_file_name'] = saved_file_name
        required_object['filled_pdf_dict_raw'] = return_dict

        pre_defined_json = self.get_preview_dict(filled_dict=filled_in_dict)
        required_object['predefined_json'] = pre_defined_json

        ## also LLM to get relevant fields to be returned to frontend for preview

        return required_object
    
    def get_preview_dict(self, filled_dict):
        prompt = self.fill_predefined_json(filled_dict)
        result = self.invoking_gemini(None, prompt)
        return json.loads(result)
    
    def fill_fields_prompt(self, fields, source_info: str) -> str:
        return f"""
            You are a seasoned PyMuPDF developer working for a clinic and you have nursing experience
            Your job is to fill the following form fields using the provided materials.
            Field description will tell you which values they expect:
            {json.dumps(fields, indent=2)}

            Materials:
            - The following summary written by the doctor on duty
            {source_info}

            Output a list of JSON objects as follows:
        [
                'xref': <original xref>,
                'name': <original name>,
                'value': <what you decided should be value for this widget>
        ] 
        """
    def fill_predefined_json(self, filled_fields_per_page)->str:
        return f"""
            You are a seasoned PyMuPDF developer working for a clinic and you have nursing experience
            Your job is to translate the raw PyMuPDF widget values into a human-readable JSON
            Field description what each values they represent:
            {filled_fields_per_page}

            Output a single JSON objects as follows, if that value was not given, DO NOT make up values for it:
                "PatientAdmissionDate": "",
                "PatientDischargeDate": "",
                "HospitalName": "",
                "HospitalAddress": "",
                "ReasonForHospitalization": "",
                "DiagnosisCodeICD10Codes": "",
                "TreatmentDescription": "",
                "AttendingDoctorName": "",
                "AttendingDoctorRegistrationNumber": "",
                "DischargeStatus": "",
                "PrescribedMedicine": "",
                "InvestigationsConducted": ""
        """
    
    def invoking_gemini(self, 
                        path_to_image, prompt, max_retries=10, retry_count=0):
        
        client = self.client

        try:
            start_time = time.time()  # record start time

            if path_to_image is not None:
                myfile = client.files.upload(file=path_to_image)
                contents = [myfile, "\n\n", prompt]
            else:
                contents = ["\n\n", prompt]

            result = client.models.generate_content(
                # model="gemini-2.5-pro",
                model = "gemini-2.0-flash",
                contents=contents,
                config={"response_mime_type": "application/json"}
            )
            end_time = time.time()  # record end time
            duration = end_time - start_time
            print(f"This successful call to LLM took {duration:.4f} seconds")

            return result.text

        except genai.errors.APIError as e:
            if hasattr(e, "code") and e.code in [429, 500, 502, 503]:
                print(f"retrying for {retry_count}")
                end_time = time.time()  # record end time
                duration = end_time - start_time
                print(f"This unsuccessful call to LLM took {duration:.4f} seconds")
                if retry_count < max_retries:
                    # wait_time = 2 ** retry_count  # exponential backoff: 1s, 2s, 4s, ...
                    # time.sleep(wait_time)
                    return self.invoking_gemini(path_to_image, prompt, max_retries, retry_count + 1)
                else:
                    print(f"Max retries reached ({max_retries}). Raising exception.")
                    raise
            else:
                raise
    
    def get_schema(self, filenamepdf):
        #csv example for quick demo

        # __file__ = .../app/services/auto_fill_service.py
        # base_dir = Path(__file__).resolve().parent.parent  # goes up from services/ to app/
        # csv_path = base_dir / "data_schema_20250714_165434_updated.csv"

        data_schema_df = pd.read_csv(self.csv_path)
        data_schema_df['data_schema_pdf_raw'] = data_schema_df['data_schema_pdf_raw'].apply(json.loads)

        required_schema = data_schema_df.loc[data_schema_df['filename']==filenamepdf, 'data_schema_pdf_raw']

        if not required_schema.empty:
            result = required_schema.iloc[0]
            return result
        else:
            raise ValueError("No such schema")
        

    def find_xref_index(self, xref, data):
        for index, item in enumerate(data):
            if item['xref'] == xref:
                return index


    def update_pdf_fields(self, updated_field:list, filename:str):
        pdf_document = fitz.open(self.filled_in_pdf_template_dir / filename)
        # print(f'The document should have these page_index {updated_field.keys()}')
        # print(f'The document has {len(updated_field)}')
        print(f"updating {filename}")


        to_update_dict_list = {int(e['id'].split("_")[0]): e for e in updated_field}


        for pageNum in range(0, len(pdf_document)):
            page = pdf_document.load_page(pageNum)
            widget_list = page.widgets()

            if widget_list:
                for widget in widget_list:

                    xref = widget.xref

                    # for jsonObject in updated_field:
                    #     currentXref = jsonObject['id'].split("_")[0]
                    #     print(f"currentXref is {currentXref}")

                    #     if currentXref == xref:
                    #         widget.field_value = jsonObject['value']
                    #         widget.update()
                
                    if xref in to_update_dict_list:
                        print(f'updating xref id: {xref}')
                        widget.field_value = to_update_dict_list[xref].get('value')
                        widget.update()

        
        ## overwrite previous PDF if update mode
        saved_file_name = filename
        pdf_document.save(self.filled_in_pdf_template_dir / filename, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        pdf_document.close()
        return saved_file_name




    def fill_pdf_fields(self, filled_in_dict:dict, filename: str):


        ## create mode vs update mode -> else
        pdf_document = fitz.open(self.pdf_template_dir / filename)

        print(f'The document should have these page_index {filled_in_dict.keys()}')
        print(f'The document has {len(pdf_document)}')

        list_string = list(filled_in_dict.keys())
        page_int_list = [int(x) for x in list_string]

        for page_num in list(filled_in_dict.keys()):

            print(f"current page num: {page_num}")
            list_string_index = list_string.index(page_num)
            page = pdf_document.load_page(page_int_list[list_string_index])
            widget_list = page.widgets()
            
            field_value_page = json.loads(filled_in_dict[page_num])

            if widget_list:
                for widget in widget_list:

                    xref = widget.xref
                    index = self.find_xref_index(xref=xref,data=field_value_page)
                    print(f'currnet xref and inde: {xref} - {index}')

                    if index is not None:
                        widget.field_value = field_value_page[index]['value']
                        widget.update()
                    # if xref in field_xref:

                    #     index = find_xref_index

                    #     widget.field_value = field_values[field_name]
                    #     widget.update()

        ## create mode vs update mode -> else

        saved_file_name = f'{filename}_filled_at_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf_document.save(self.filled_in_pdf_template_dir / saved_file_name)
        pdf_document.close()
        return saved_file_name

