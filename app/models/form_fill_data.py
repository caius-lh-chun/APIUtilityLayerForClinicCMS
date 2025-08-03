from pydantic import BaseModel, Field

class FormRequest(BaseModel):
    summary: str = Field(..., example=""""Based on the comprehensive review of Lai hin hei's selected medical records from 2019, the following summary has been prepared for insurance claim purposes:\n\nPATIENT INFORMATION:\nPatient Name: Lai hin hei\nSelected Records for Analysis: 3\nPrimary Review Period: March 2019 - April 2019\n\nMEDICAL HISTORY SUMMARY:\nThe patient presents with a documented history of gastrointestinal issues requiring specialized investigation and treatment. Key findings from the selected consultation records include:\n\n1. INITIAL PRESENTATION (13/03/2019):\n   - Chief Complaint: Epigastric pain for 2 months with regurgitation and belching\n   - Patient History: Non-smoker, social drinker, no known drug allergies, good past health\n   - Clinical Assessment: General condition satisfactory, no pallor, no lymphadenopathy, no jaundice\n   - Abdominal Examination: Soft abdomen, no palpable masses\n   - Diagnosis: Epigastric pain and regurgitation\n   - Management Plan: Scheduled for OGD (Oesophagogastroduodenoscopy), intravenous sedation\n\n2. DIAGNOSTIC PROCEDURE (28/03/2019):\n   - Procedure: Endoscopy (OGD) performed under proper clinical supervision\n   - Findings: Gastritis and duodenitis identified\n   - Laboratory Tests: CLO test negative, tissue biopsy performed\n   - Pathology Results: No intestinal metaplasia, no Helicobacter pylori detected\n   - Clinical Significance: Definitive diagnosis established through appropriate investigation\n\n3. FOLLOW-UP CONSULTATION (04/04/2019):\n   - Patient Response: Significant symptom improvement noted\n   - Clinical Status: Continued monitoring of gastritis and duodenitis\n   - Treatment Outcome: Positive response to initial management\n   - Follow-up Plan: Return as needed (PRN) basis\n\nTREATMENT APPROACH:\n- Evidence-based diagnostic workup with endoscopic evaluation\n- Appropriate use of pathological testing to rule out serious conditions\n- Conservative management approach with medication therapy\n- Structured follow-up protocol ensuring continuity of care\n\nFINANCIAL SUMMARY FOR SELECTED RECORDS:\n- Endoscopy (OGD): $6,000\n- Operation Theatre Fee: $1,800  \n- Pathology Services: $1,000\n- Medication: $130\n- Consultation Fees: Provided free of charge\nTotal Medical Expenses: $8,930\n\nCLAIM ASSESSMENT:\nThis case demonstrates appropriate medical management of gastrointestinal symptoms with:\n✓ Proper clinical evaluation and examination\n✓ Medically necessary diagnostic procedures\n✓ Evidence-based treatment approach\n✓ Appropriate follow-up care\n\nRECOMMENDATION:\nThe selected consultation records support the medical necessity of the treatments provided. The diagnostic approach was appropriate for the presenting symptoms, and the endoscopic evaluation was clinically indicated. All charges are reasonable and customary for the procedures performed.\n\nThis analysis supports approval for the associated medical expenses related to the investigation and management of the patient's gastrointestinal condition during the specified period.""")
    pdf_name: str = Field(..., example="AIA hospital OPCLMF03.pdf.coredownload.inline.pdf")

class FormResponse(BaseModel):
    # filename: str = Field(..., example="AIA hospital OPCLMF03.pdf.coredownload.inline.pdf_filled_at_20250801_075306.pdf")
    filled_pdf_dict: dict = Field(..., example = 
            {
                "259_rbQ8": None,
                "266_rbQ8": None,
                "233_txtID": None,
                "255_txtQ6": "Back sebaceous cyst",
                "261_txtQ7": "Excision of back mass under Local Anesthesia (LA)",
                "275_txtQ3": "Back nodule x 2 months, possible pain, increase in size.",
                "281_rbQ9f": "Yes"
            }         
                                  )

class FormUpdateRequest(BaseModel):
    ticket_id: str = Field(..., example = "dcd924cb-60a3-4756-b94a-9695002de8e8")
    # form_id: str = Field(..., example = "aia-opclmf03")
    pdf_name: str = Field(..., example = "AIA hospital OPCLMF03.pdf.coredownload.inline.pdf")
    form_data: dict = Field(..., example = 
            {
                "259_rbQ8": None,
                "266_rbQ8": None,
                "233_txtID": None,
                "255_txtQ6": "Back sebaceous cyst",
                "261_txtQ7": "Excision of back mass under Local Anesthesia (LA)",
                "275_txtQ3": "Back nodule x 2 months, possible pain, increase in size.",
                "281_rbQ9f": "Yes"
            }         
                                  )
    
class FormUpdateResponse(BaseModel):
    form_snapshots_id: str = Field(..., example = "24a72aa8-1b61-4c0e-ac07-d868c83c7622")
    form_snapshots_message: str = Field(..., example = "Form Snapshots ID 24a72aa8-1b61-4c0e-ac07-d868c83c7622 Version 4 has been created")


class DownloadRequest(BaseModel):
    ticket_id: str = Field(..., example = "24a72aa8-1b61-4c0e-ac07-d868c83c7622")