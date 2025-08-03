import pandas as pd
import json
from app.models.form_fill_data import *
from app.models.data_enums import *
from app.models.supbase_form_snapshot import *
from fastapi.responses import FileResponse,StreamingResponse
from pathlib import Path
from google import genai
from datetime import datetime
from dotenv import load_dotenv
from . import supabase_service, gemini_service
from io import BytesIO
import time
import fitz
import os
from ..prompts import auto_fill_prompts

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
    supa_base_mode = os.getenv("SUPABASE_MODE")
    client = genai.Client(api_key=api_key)


    def __init__(self):
        # Initialize service dependencies here (e.g., DB, external APIs)
        pass

    def download_pdf(self, request:DownloadRequest):

        # template_filename = filename.split("_")[0]

        ticket_id = request.ticket_id
        if self.supa_base_mode:

            
            ## get template then retrieve latest field_list dict for update and real time fill for download

            latest_version_record = supabase_service.get_latest_version_of_form_snapshots(ticket_id)
            template_filename = latest_version_record['pdf_file_name']
            print(f"current template is {template_filename}")
            updated_field = latest_version_record['form_data']
            print(f"current update field is {updated_field}")

            file_bytes = supabase_service.download_from_supabase_storage_form_templates(template_filename)
            # updated_field = json.loads(supabase_service.get_filled_record_from_supabase(filename))['field_list']
            
            pdf_document = fitz.open(stream=file_bytes)

            # {
            #     "259_rbQ8": null,
            #     "266_rbQ8": null,
            #     "233_txtID": null,
            #     "255_txtQ6": "Back sebaceous cyst",
            #     "261_txtQ7": "Excision of back mass under Local Anesthesia (LA)"
            # }

            to_update_dict_list = {}

            for key, value in updated_field.items():
                append_key = int(key.split("_")[0])
                to_update_dict_list[append_key] = value


            # to_update_dict_list = {int(e['id'].split("_")[0]): e for e in updated_field}

            
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
                    
                        if xref in to_update_dict_list.keys():
                            print(f'updating xref id: {xref}')
                            widget.field_value = to_update_dict_list[xref]
                            widget.update()

            updated_bytes = pdf_document.write()
            pdf_document.close()

            # Wrap bytes in a BytesIO stream for StreamingResponse
            file_like = BytesIO(updated_bytes)

            return StreamingResponse(
                file_like,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={template_filename}_{ticket_id}.pdf"
                }
            )

    def update_form(self, update_dto):

        # class FormUpdateRequest(BaseModel):
        #     ticket_id: str = Field(..., example = "dcd924cb-60a3-4756-b94a-9695002de8e8")
        #     form_id: str = Field(..., example = "aia-opclmf03")
        #     pdf_name: str = Field(..., example = "AIA hospital OPCLMF03.pdf.coredownload.inline.pdf")
        #     form_data: dict = Field(..., example = 
        #             {
        #                 "259_rbQ8": None,
        #                 "266_rbQ8": None,
        #                 "233_txtID": None,
        #                 "255_txtQ6": "Back sebaceous cyst",
        #                 "261_txtQ7": "Excision of back mass under Local Anesthesia (LA)",
        #                 "275_txtQ3": "Back nodule x 2 months, possible pain, increase in size.",
        #                 "281_rbQ9f": "Yes"
        #             }         
        #                                 )
            
        # class FormUpdateResponse(BaseModel):
        #     form_snapshots_id: str = Field(..., example = "24a72aa8-1b61-4c0e-ac07-d868c83c7622")
        #     form_snapshots_message: str = Field(..., example = "Form Snapshots ID 24a72aa8-1b61-4c0e-ac07-d868c83c7622 Version 4 has been created")


        template_name = update_dto.pdf_name #template name to find Enums
        # form_id = update_dto.form_id #form_id (optional) -> depends which one Eric wants to search by
        ## find by form_id whether have or not first, if not insert a new version starting zero
        form_data_dict = update_dto.form_data #the form_data JSON
        ticket_id = update_dto.ticket_id

        current_ticket_form_snapshots = supabase_service.search_form_snapshots_by_ticket_id(ticket_id)
        current_form_enum = form_templates.find_by_filename(template_name)

        if len(current_ticket_form_snapshots) == 0:
            
            print("Create new snapshots")
            current_version = 1

            formSnapshot = FormSnapshot(
                ticket_id= ticket_id,
                form_id = current_form_enum.form_id,
                insurance_company=current_form_enum.company_name,
                pdf_file_name= current_form_enum.template_name,
                form_name= current_form_enum.form_name,
                form_data= form_data_dict,
                version=current_version,
                status= 'draft' # assume start from 1
            )

            response = supabase_service.insert_new_form_snapshots_for_update(formSnapshot)

            print(response)

            if response:
                return FormUpdateResponse(
                    form_snapshots_id=response[0]['id'],
                    form_snapshots_message= f"Form Snapshots ID {response[0]['id']} Version {current_version} has been created")
        else:

            current_version = len(current_ticket_form_snapshots) + 1

            formSnapshot = FormSnapshot(
                ticket_id= ticket_id,
                form_id = current_form_enum.form_id,
                insurance_company=current_form_enum.company_name,
                form_name= current_form_enum.form_name,
                pdf_file_name= current_form_enum.template_name,
                form_data= form_data_dict,
                version=current_version, # assume start from 1
                status= 'draft'
            )

            response = supabase_service.insert_new_form_snapshots_for_update(formSnapshot)

            print(response)

            if response:
                return FormUpdateResponse(
                    form_snapshots_id=response[0]['id'],
                    form_snapshots_message= f"Form Snapshots ID {response[0]['id']} Version {current_version} has been created")


        # class FormSnapshot(BaseModel):
        #     ticket_id: str ##UUID
        #     form_id: str
        #     insurance_company: str
        #     form_name: str
        #     form_data: dict
        #     pdf_file_name: str
        #     version: int
        #     status: str ## status logic?
        #     ## optional created at and updated at date, ride on default create behavior?


        # saved_file_name = self.update_pdf_fields(list_for_update_widget, filename)

        # required_object['filled_pdf_file_name'] = saved_file_name

        # return required_object


    def process_form(self, form_data: FormRequest) -> FormResponse:


        filename = form_data.pdf_name
        print(f"processing {filename}")
        summary = form_data.summary
        print(f"received summary {summary}")

        pdf_schema = self.get_schema(filenamepdf=f'{filename}')
        print(f"retried schema")

        ## after get schema, fill in PDF and save somewhere and return defined fields from here
        filled_in_dict = {}
        transformed_schema = {}

        for page, widgets in pdf_schema.items():
            ## get a transformed schema
            for e in widgets:
                transformed_schema[e['id']] = e['description']

        print(f"schema transformed as: {transformed_schema}")
        prompt_for_task = auto_fill_prompts.fill_fields_prompt(transformed_schema,summary)
        result = gemini_service.invoking_gemini(path_to_image=None, prompt=prompt_for_task)

        ## this part change to whole file at once
        # for page, widget in pdf_schema.items():
        #     prompt_for_task = auto_fill_prompts.fill_fields_prompt(widget,summary)
        #     result = gemini_service.invoking_gemini(path_to_image=None, prompt=prompt_for_task)
        #     filled_in_dict[page] = result

        ## after load json, add id for each element
        print(f"from LLM: {result}")

        dict_result = json.loads(result)

        # return_dict = {
        #     "field_list" : []
        # }

        for page, widgets in pdf_schema.items():
            ## get a composed filled / not filled schema
            for e in widgets:
                if e['id'] not in list(dict_result.keys()):
                    dict_result[e['id']] = None


        # for page, pageJsonList in filled_in_dict.items():
            
        #     pageJsonList = json.loads(pageJsonList)
        #     pageJsonDict = {e['xref']: e for e in pageJsonList}

        #     for x in pdf_schema[page]:
        #         toFillXref = x['xref']
        #         newObject = {
        #             'id': f"{toFillXref}_{x['name']}",
        #             'value': None  # default
        #         }
                
        #         if toFillXref in pageJsonDict:
        #             newObject['value'] = pageJsonDict[toFillXref].get('value')
                
        #         return_dict["field_list"].append(newObject)
            
        # saved_file_name = self.fill_pdf_fields(filled_in_dict=filled_in_dict,filename=filename)

        saved_file_name = f'{filename}_filled_at_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        print(f"saved PDF as {saved_file_name}")


        # required_object['filled_pdf_file_name'] = saved_file_name
        # required_object['filled_pdf_dict_raw'] = return_dict

        # if self.supa_base_mode:
        #     saved_response = supabase_service.insert_filled_record_to_supabase(saved_file_name, return_dict)

        # pre_defined_json = self.get_preview_dict(filled_dict=filled_in_dict)
        # required_object['predefined_json'] = pre_defined_json

        ## also LLM to get relevant fields to be returned to frontend for preview

        

        formResponse = FormResponse(filled_pdf_dict = dict_result)
        
        print(f"result returned: \n {formResponse.model_dump()}")

        return formResponse
    
    
    def get_schema(self, filenamepdf):
        if self.supa_base_mode:
            ## return the json.loads of data_schema_pdf_raw
            return json.loads(supabase_service.search_pdf_schema_by_filename(filenamepdf))
        

    def find_xref_index(self, xref, data):
        for index, item in enumerate(data):
            if item['xref'] == xref:
                return index


    ## TODO: rewrite logic as follows:
    ## take in ticket id, form-id (get from Enum)
    def update_pdf_fields(self, updated_field:list, filename:str):

        if self.supa_base_mode:

            required_dict = {'field_list':updated_field}
            update_response = supabase_service.update_filled_record(filename, required_dict)

        saved_file_name = filename

        return saved_file_name




    def fill_pdf_fields(self, filled_in_dict:dict, filename: str):

        ## create mode vs update mode -> else

        if self.supa_base_mode:
            pdf_document_bytes = supabase_service.download_from_supabase_storage_form_templates(filename)
            pdf_document = fitz.open(stream=pdf_document_bytes)

        else:
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


        saved_file_name = f'{filename}_filled_at_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        # if self.supa_base_mode:
        #     pdf_document_bytes_to_be_saved = pdf_document.write()
        #     supabase_result = supabase_service.update_to_supabase_filled_forms(pdf_document_bytes_to_be_saved,
        #                                                                        saved_file_name)
        # else:
        #     pdf_document.save(self.filled_in_pdf_template_dir / saved_file_name)

        
        pdf_document.close()
        return saved_file_name

