from typing import Optional, List
from datetime import datetime, date

# Minimal schemas for basic functionality
class UserBase:
    def __init__(self, username: str, email: str, full_name: str):
        self.username = username
        self.email = email
        self.full_name = full_name

class UserCreate(UserBase):
    def __init__(self, username: str, email: str, full_name: str, password: str):
        super().__init__(username, email, full_name)
        self.password = password

class User(UserBase):
    def __init__(self, id: int, username: str, email: str, full_name: str, is_active: bool, created_at: datetime, updated_at: datetime):
        super().__init__(username, email, full_name)
        self.id = id
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

class LoginCredentials:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

class Token:
    def __init__(self, access_token: str, token_type: str):
        self.access_token = access_token
        self.token_type = token_type

class SARCreate:
    def __init__(self, organization_name: str, request_type: str, request_description: str, submission_date: date, submission_method: str, custom_deadline: Optional[date] = None):
        self.organization_name = organization_name
        self.request_type = request_type
        self.request_description = request_description
        self.submission_date = submission_date
        self.submission_method = submission_method
        self.custom_deadline = custom_deadline

class SARCase:
    def __init__(self, id: int, case_reference: str, user_id: int, organization_name: str, request_type: str, request_description: str, submission_date: date, submission_method: str, statutory_deadline: date, status: str, created_at: datetime, updated_at: datetime):
        self.id = id
        self.case_reference = case_reference
        self.user_id = user_id
        self.organization_name = organization_name
        self.request_type = request_type
        self.request_description = request_description
        self.submission_date = submission_date
        self.submission_method = submission_method
        self.statutory_deadline = statutory_deadline
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
