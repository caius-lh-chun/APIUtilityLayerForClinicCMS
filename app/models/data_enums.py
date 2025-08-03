from enum import Enum


class form_templates(Enum):
    AIA_OPCLMF03 = ("aia-opclmf03", "AIA", "AIA Hospital Claim Form (OPCLMF03)", "AIA hospital OPCLMF03.pdf.coredownload.inline.pdf")
    PRU_HOSPITAL_CLAIM_FORM = ("pru-hos-claim", "Prudential", "Prudential Hospital Claim Form", "Prudential hospital claim form.pdf")
    AXA_HOSPITAL_CLAIM_FORM_GE_HK_FILLABLE = ("axa-hos-ge-hk-fillable", "AXA", "AXA Hospital Claim Form GE HK Fillable", "AXA hospitalization Claim Form -GE_HK_Fillable.pdf")
    AXA_PERSONAL_CLAIM_FORM_I = ("axa-personal-claim-form-i", "AXA", "AXA Personal Claim Form I", "AXA Personal Claim Form I.pdf")
    AXA_LFC032_2111 = ("axa-lfc032-2111", "AXA", "AXA LFC032 2111", "AXA LFC032_2111_disability-accident-hospitalisation-claim-form-ii_v4_fillable_chi.pdf")


    def __init__(self, form_id, company_name, form_name, template_name):
        self._form_id = form_id
        self._company_name = company_name
        self._form_name = form_name
        self._template_name = template_name

    @property
    def form_id(self):
        return self._form_id

    @property
    def company_name(self):
        return self._company_name

    @property
    def form_name(self):
        return self._form_name

    @property
    def template_name(self):
        return self._template_name

    @classmethod
    def find_by_filename(cls, filename: str):
        for member in cls:
            if member.template_name == filename:
                return member
        raise ValueError(f"No form template found with filename {filename}")