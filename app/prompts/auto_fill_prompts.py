import json

def fill_fields_prompt(fields, source_info: str) -> str:
    return f"""

        ## Your role
        You are a seasoned PyMuPDF developer working for a clinic and you have nursing experience
        Your job is to fill the following claim form fields using the provided materials.

        ## Your input
        - The following is a JSON of PDF widget ID to widget description pairing, please use this to see what each field should be filled
        ```{json.dumps(fields, indent=2)}```
        - The following summary written by the doctor on duty
        ```{source_info}```

        ## Your task:
        - Study the JSON of PDF widget provided, understand each key and the description of that particular widget field
        - Based on the description of the widget, please fill in the form as best as you can, here are some DOs and DONTs
            - DOs:
                - try to fill all patients information such as Name, ID number and other PII type data
                - If available, please fill in hospitals, admission date, discharge date, chief complaints, symptoms first appeared, date of first consultation, final diagnosis, surgical procedure OR medical procedure
                - If both fields are available, date of operation MUST be equal to date of admission / admission date
                - Name of procedures, medical surgery and discharge summary must be filled if available
                - If asked whether the patient referred to by another doctor, the answer MUST be a negative
                - If asked whether the patient has Similar conditions in history, the answer MUST be a negative
                - If asked whether the patient suffered from Cancer, the answer MUST be a negative
            - DONTs:
                - DO NOT make up anwer or say the answer is not specified in notes if you cannot answer, please leave all unsure answers as blank
                - Never write "Not specified in notes" or equivalent for answer you are not sure about or are indeed not provided

        Output a JSON object as follows:
            ```
                "widget_id_#1" : "value it should be",
                "widget_id_#2" : "value it should be filled as",
                .
                .
                .
                .
                .
                "widget_id_#n" : "value it should be filled as"
            ```

    """


    # def fill_predefined_json(self, filled_fields_per_page)->str:
    #     return f"""
    #         You are a seasoned PyMuPDF developer working for a clinic and you have nursing experience
    #         Your job is to translate the raw PyMuPDF widget values into a human-readable JSON
    #         Field description what each values they represent:
    #         {filled_fields_per_page}

    #         Output a single JSON objects as follows, if that value was not given, DO NOT make up values for it:
    #             "PatientAdmissionDate": "",
    #             "PatientDischargeDate": "",
    #             "HospitalName": "",
    #             "HospitalAddress": "",
    #             "ReasonForHospitalization": "",
    #             "DiagnosisCodeICD10Codes": "",
    #             "TreatmentDescription": "",
    #             "AttendingDoctorName": "",
    #             "AttendingDoctorRegistrationNumber": "",
    #             "DischargeStatus": "",
    #             "PrescribedMedicine": "",
    #             "InvestigationsConducted": ""
    #     """