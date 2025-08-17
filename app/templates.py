from datetime import datetime, date
from typing import Dict, Any
from app.schemas import SARCase

def get_sar_template() -> Dict[str, Any]:
    """Get the SAR request template with placeholders."""
    template = """
Subject: Subject Access Request - [ORGANIZATION_NAME]

Dear [CONTACT_NAME],

I am writing to make a Subject Access Request under the Data Protection Act 2018 and UK GDPR.

**Personal Details:**
- Full Name: [FULL_NAME]
- Date of Birth: [DATE_OF_BIRTH]
- Address: [ADDRESS]
- Email: [EMAIL]
- Phone: [PHONE]

**Request Details:**
I am requesting access to all personal data that [ORGANIZATION_NAME] holds about me, including but not limited to:

[REQUEST_DETAILS]

**Requested Format:**
I would prefer to receive this information in [FORMAT_PREFERENCE] format.

**Timeline:**
Under UK GDPR, you are required to respond to this request within one calendar month (28 days) of receipt. If you need an extension, you must inform me within the initial timeframe and provide a valid reason.

**Contact Information:**
Please send your response to:
Email: [EMAIL]
Address: [ADDRESS]

**Reference Number:**
Please quote reference: [CASE_REFERENCE] in all correspondence.

I look forward to receiving your response within the statutory timeframe.

Yours sincerely,
[FULL_NAME]

---
This request is made under Article 15 of the UK GDPR and Section 45 of the Data Protection Act 2018.
    """
    
    placeholders = [
        "ORGANIZATION_NAME",
        "CONTACT_NAME", 
        "FULL_NAME",
        "DATE_OF_BIRTH",
        "ADDRESS",
        "EMAIL",
        "PHONE",
        "REQUEST_DETAILS",
        "FORMAT_PREFERENCE",
        "CASE_REFERENCE"
    ]
    
    return {
        "template": template.strip(),
        "placeholders": placeholders,
        "description": "Standard SAR request template with all required elements"
    }

def get_followup_template() -> Dict[str, Any]:
    """Get the follow-up email template for overdue cases."""
    template = """
Subject: Follow-up: Subject Access Request [CASE_REFERENCE] - [ORGANIZATION_NAME]

Dear [CONTACT_NAME],

I am writing to follow up on my Subject Access Request dated [SUBMISSION_DATE] (reference: [CASE_REFERENCE]).

**Current Status:**
- Original submission date: [SUBMISSION_DATE]
- Statutory deadline: [STATUTORY_DEADLINE]
- Days overdue: [DAYS_OVERDUE]

**Request Summary:**
[REQUEST_DESCRIPTION]

**Action Required:**
As of today, this request is [DAYS_OVERDUE] days overdue. Under UK GDPR, you are legally required to respond within one calendar month of receipt.

Please provide:
1. An immediate update on the status of my request
2. A firm date when I can expect to receive the requested information
3. An explanation for any delay, if applicable

**Next Steps:**
If I do not receive a satisfactory response within [FOLLOW_UP_DAYS] days, I will be forced to escalate this matter to the Information Commissioner's Office (ICO) for investigation.

**Contact Information:**
Please respond to: [EMAIL]

I look forward to your prompt response.

Yours sincerely,
[FULL_NAME]

---
This follow-up is in relation to Article 15 of the UK GDPR and Section 45 of the Data Protection Act 2018.
    """
    
    placeholders = [
        "CASE_REFERENCE",
        "ORGANIZATION_NAME",
        "CONTACT_NAME",
        "SUBMISSION_DATE",
        "STATUTORY_DEADLINE",
        "DAYS_OVERDUE",
        "REQUEST_DESCRIPTION",
        "FOLLOW_UP_DAYS",
        "EMAIL",
        "FULL_NAME"
    ]
    
    return {
        "template": template.strip(),
        "placeholders": placeholders,
        "description": "Follow-up template for overdue SAR requests"
    }

def get_ico_escalation_template() -> Dict[str, Any]:
    """Get the ICO escalation template with case details."""
    template = """
Subject: ICO Complaint - Failure to Respond to Subject Access Request

Dear Information Commissioner's Office,

I am writing to lodge a formal complaint against [ORGANIZATION_NAME] for their failure to respond to my Subject Access Request within the statutory timeframe.

**Complaint Details:**

**Personal Information:**
- Complainant: [FULL_NAME]
- Address: [ADDRESS]
- Email: [EMAIL]
- Phone: [PHONE]

**Organization Details:**
- Organization: [ORGANIZATION_NAME]
- Address: [ORGANIZATION_ADDRESS]
- Email: [ORGANIZATION_EMAIL]
- Phone: [ORGANIZATION_PHONE]

**Subject Access Request Details:**
- Case Reference: [CASE_REFERENCE]
- Submission Date: [SUBMISSION_DATE]
- Submission Method: [SUBMISSION_METHOD]
- Statutory Deadline: [STATUTORY_DEADLINE]
- Days Overdue: [DAYS_OVERDUE]

**Request Description:**
[REQUEST_DESCRIPTION]

**Timeline of Events:**
1. [SUBMISSION_DATE] - SAR submitted to [ORGANIZATION_NAME]
2. [STATUTORY_DEADLINE] - Statutory deadline passed
3. [CURRENT_DATE] - No response received to date

**Correspondence History:**
[CORRESPONDENCE_SUMMARY]

**Grounds for Complaint:**
1. **Breach of Article 15 UK GDPR**: Failure to provide access to personal data within one month
2. **Breach of Section 45 DPA 2018**: Failure to comply with SAR requirements
3. **Lack of Communication**: No acknowledgment or explanation for delay
4. **No Extension Request**: Organization did not request an extension within the statutory timeframe

**Impact:**
This failure has caused me [IMPACT_DESCRIPTION] and represents a significant breach of my data protection rights.

**Requested Action:**
I request that the ICO:
1. Investigate this complaint thoroughly
2. Require [ORGANIZATION_NAME] to respond to my SAR within a specified timeframe
3. Take appropriate enforcement action if necessary
4. Provide me with regular updates on the investigation

**Supporting Documentation:**
I have attached copies of:
- Original SAR submission
- All correspondence with [ORGANIZATION_NAME]
- Evidence of submission (emails, postal receipts, etc.)

**Declaration:**
I confirm that the information provided in this complaint is accurate to the best of my knowledge.

Yours sincerely,
[FULL_NAME]

---
This complaint is made under Section 165 of the Data Protection Act 2018.
    """
    
    placeholders = [
        "ORGANIZATION_NAME",
        "FULL_NAME",
        "ADDRESS", 
        "EMAIL",
        "PHONE",
        "ORGANIZATION_ADDRESS",
        "ORGANIZATION_EMAIL",
        "ORGANIZATION_PHONE",
        "CASE_REFERENCE",
        "SUBMISSION_DATE",
        "SUBMISSION_METHOD",
        "STATUTORY_DEADLINE",
        "DAYS_OVERDUE",
        "REQUEST_DESCRIPTION",
        "CURRENT_DATE",
        "CORRESPONDENCE_SUMMARY",
        "IMPACT_DESCRIPTION"
    ]
    
    return {
        "template": template.strip(),
        "placeholders": placeholders,
        "description": "ICO escalation complaint template with comprehensive case details"
    }

def get_reminder_template() -> Dict[str, Any]:
    """Get the reminder template for upcoming deadlines."""
    template = """
Subject: Reminder: SAR Deadline Approaching - [CASE_REFERENCE]

Dear [FULL_NAME],

This is a reminder about your upcoming Subject Access Request deadline.

**Case Details:**
- Case Reference: [CASE_REFERENCE]
- Organization: [ORGANIZATION_NAME]
- Submission Date: [SUBMISSION_DATE]
- Deadline: [DEADLINE_DATE]
- Days Remaining: [DAYS_REMAINING]

**Action Required:**
- If you haven't received a response: Prepare follow-up communication
- If you received a response: Review and update case status
- If response is incomplete: Prepare follow-up request

**Next Steps:**
1. Check if you've received a response
2. Review the response for completeness
3. Update your case file with any new information
4. Consider next actions based on the response

**Template Available:**
Use the follow-up template if you need to send a reminder email.

**Contact:**
If you have any questions about this case, please refer to your case file.

---
This is an automated reminder from your SAR Tracking System.
    """
    
    placeholders = [
        "FULL_NAME",
        "CASE_REFERENCE",
        "ORGANIZATION_NAME",
        "SUBMISSION_DATE",
        "DEADLINE_DATE",
        "DAYS_REMAINING"
    ]
    
    return {
        "template": template.strip(),
        "placeholders": placeholders,
        "description": "Reminder template for upcoming deadlines"
    }

def populate_template(template: str, data: Dict[str, Any]) -> str:
    """Populate a template with actual data."""
    populated = template
    
    for placeholder, value in data.items():
        if value is not None:
            if isinstance(value, date):
                value = value.strftime("%d/%m/%Y")
            elif isinstance(value, datetime):
                value = value.strftime("%d/%m/%Y %H:%M")
            
            populated = populated.replace(f"[{placeholder}]", str(value))
    
    return populated

def get_sar_email_content(sar_case: SARCase, user_data: Dict[str, Any]) -> str:
    """Generate SAR email content from template and case data."""
    template_data = get_sar_template()
    
    # Prepare data for template
    data = {
        "ORGANIZATION_NAME": sar_case.organization_name,
        "CONTACT_NAME": "Data Protection Officer",  # Default
        "FULL_NAME": user_data.get("full_name", "Your Name"),
        "DATE_OF_BIRTH": user_data.get("date_of_birth", "[DATE_OF_BIRTH]"),
        "ADDRESS": user_data.get("address", "[ADDRESS]"),
        "EMAIL": user_data.get("email", "[EMAIL]"),
        "PHONE": user_data.get("phone", "[PHONE]"),
        "REQUEST_DETAILS": sar_case.request_description,
        "FORMAT_PREFERENCE": "electronic",
        "CASE_REFERENCE": sar_case.case_reference
    }
    
    return populate_template(template_data["template"], data)

def get_followup_email_content(sar_case: SARCase, user_data: Dict[str, Any], days_overdue: int) -> str:
    """Generate follow-up email content from template and case data."""
    template_data = get_followup_template()
    
    # Calculate days overdue
    current_date = date.today()
    deadline = sar_case.extended_deadline or sar_case.custom_deadline or sar_case.statutory_deadline
    
    data = {
        "CASE_REFERENCE": sar_case.case_reference,
        "ORGANIZATION_NAME": sar_case.organization_name,
        "CONTACT_NAME": "Data Protection Officer",
        "SUBMISSION_DATE": sar_case.submission_date,
        "STATUTORY_DEADLINE": sar_case.statutory_deadline,
        "DAYS_OVERDUE": days_overdue,
        "REQUEST_DESCRIPTION": sar_case.request_description,
        "FOLLOW_UP_DAYS": "7",
        "EMAIL": user_data.get("email", "[EMAIL]"),
        "FULL_NAME": user_data.get("full_name", "Your Name")
    }
    
    return populate_template(template_data["template"], data)

def get_ico_complaint_content(sar_case: SARCase, user_data: Dict[str, Any], correspondence_summary: str) -> str:
    """Generate ICO complaint content from template and case data."""
    template_data = get_ico_escalation_template()
    
    # Calculate days overdue
    current_date = date.today()
    deadline = sar_case.extended_deadline or sar_case.custom_deadline or sar_case.statutory_deadline
    days_overdue = (current_date - deadline).days
    
    data = {
        "ORGANIZATION_NAME": sar_case.organization_name,
        "FULL_NAME": user_data.get("full_name", "Your Name"),
        "ADDRESS": user_data.get("address", "[ADDRESS]"),
        "EMAIL": user_data.get("email", "[EMAIL]"),
        "PHONE": user_data.get("phone", "[PHONE]"),
        "ORGANIZATION_ADDRESS": sar_case.organization_address or "[ORGANIZATION_ADDRESS]",
        "ORGANIZATION_EMAIL": sar_case.organization_email or "[ORGANIZATION_EMAIL]",
        "ORGANIZATION_PHONE": sar_case.organization_phone or "[ORGANIZATION_PHONE]",
        "CASE_REFERENCE": sar_case.case_reference,
        "SUBMISSION_DATE": sar_case.submission_date,
        "SUBMISSION_METHOD": sar_case.submission_method,
        "STATUTORY_DEADLINE": sar_case.statutory_deadline,
        "DAYS_OVERDUE": days_overdue,
        "REQUEST_DESCRIPTION": sar_case.request_description,
        "CURRENT_DATE": current_date,
        "CORRESPONDENCE_SUMMARY": correspondence_summary,
        "IMPACT_DESCRIPTION": "delays in accessing my personal data and potential breach of my data protection rights"
    }
    
    return populate_template(template_data["template"], data)
