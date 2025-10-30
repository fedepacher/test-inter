from fastapi import Form
from datetime import datetime, date
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, EmailStr

from api.app.schema import (pagination_info_schema, institution_schema,
                 country_schema, gender_schema)
from api.app.utils.global_def import ResultEnum, StatusEnum

EXAMPLE_EMAIL: str = 'myemail@mail.com'

class AthleteId(BaseModel):
    """Represents the ID of an athlete."""
    id: int

    class Config:
        from_attributes = True


class AthleteBase(BaseModel):
    """Base athlete information with required and optional fields."""
    email: EmailStr = Field(..., example=EXAMPLE_EMAIL)
    name: str = Field(..., max_length=50, example='Alejandro')
    last_name: str = Field(..., max_length=50, example='Estocolmo')
    birthdate: Optional[date] = Field(None, description="Athlete's birth date")
    country: Optional[country_schema.Country] = Field(None, description="Athlete's country")
    document_number: Optional[str] = Field(None, max_length=50, example='111111111')
    gender: Optional[gender_schema.Gender] = Field(None, description="Athlete's gender")
    contact_number: Optional[str] = Field(None, max_length=50, example='111111111')

    class Config:
        from_attributes = True


class AthleteBasicData(AthleteId):
    """Basic athlete information for list views."""
    name: str = Field(..., max_length=50, example="John")
    last_name: str = Field(..., max_length=50, example="Doe")
    institution_id: int
    email: EmailStr = Field(..., example=EXAMPLE_EMAIL)
    updated_at: datetime = Field(default_factory=datetime.now, example="2024-11-22T12:34:56")
    updated_by: int = Field(..., example=1)
    active: bool = Field(..., example=True)
    status: StatusEnum = Field(..., example=StatusEnum.ACTIVE)


class AthleteCreated(AthleteBase):
    """Extended athlete information including performance data."""
    institution: Optional[institution_schema.InstitutionBase]


class Athlete(AthleteId, AthleteCreated):
    """Complete athlete information including system fields."""
    active: bool = Field(..., example=True)
    status: StatusEnum = Field(..., example=StatusEnum.ACTIVE)
    updated_at: datetime = Field(default_factory=datetime.now, example="2024-11-22T12:34:56")
    updated_by: int = Field(..., example=1)

    class Config:
        from_attributes = True


class AthleteInput(BaseModel):
    """Internal input data for creating or updating an athlete."""
    email: EmailStr = Field(..., example=EXAMPLE_EMAIL, description="Athlete's email address")
    name: str = Field(..., max_length=50, example='Alejandro', description="Athlete's first name")
    last_name: str = Field(..., max_length=50, example='Estocolmo', description="Athlete's last name")
    country_id: Optional[int] = Field(None, description="Country ID")
    institution_id: Optional[int] = Field(0, description="Institution ID - if 0, uses user's default")

    birthdate: Optional[date] = Field(None, description="Athlete's birth date")
    document_number: Optional[str] = Field(None, description="Document/ID number")
    gender_id: Optional[int] = Field(None, description="Gender identification")
    contact_number: Optional[str] = Field(None, description="Phone/contact number")

    class Config:
        from_attributes = True


class AthleteCreateForm(BaseModel):
    """Form for creating new athletes."""
    email: str = Field(..., description="Athlete email address")
    name: str = Field(..., description="Athlete first name")
    last_name: str = Field(..., description="Athlete last name")
    
    birthdate: Optional[str] = Field(None, description="Birth date (YYYY-MM-DD)")
    country_id: Optional[int] = Field(None, description="Country ID")
    document_number: Optional[str] = Field(None, description="Document/ID number")
    gender_id: Optional[int] = Field(None, description="Gender ID")
    contact_number: Optional[str] = Field(None, description="Contact phone number")

    @classmethod
    def as_form(
        cls,
        email: str = Form(...),
        name: str = Form(...),
        last_name: str = Form(...),
        birthdate: Optional[str] = Form(None),
        country_id: Optional[int] = Form(None),
        document_number: Optional[str] = Form(None),
        gender_id: Optional[int] = Form(None),
        contact_number: Optional[str] = Form(None),
    ):
        return cls(
            email=email, name=name, last_name=last_name, birthdate=birthdate,
            country_id=country_id, document_number=document_number,
            gender_id=gender_id, contact_number=contact_number
        )


class AthletePersonalDataForm(BaseModel):
    """Form for updating athlete personal information."""
    email: Optional[str] = Field(None, description="New email address")
    name: Optional[str] = Field(None, description="New first name")
    last_name: Optional[str] = Field(None, description="New last name")
    birthdate: Optional[str] = Field(None, description="New birth date (YYYY-MM-DD)")
    country_id: Optional[int] = Field(None, description="New country ID")
    document_number: Optional[str] = Field(None, description="New document number")
    gender_id: Optional[int] = Field(None, description="New gender ID")
    contact_number: Optional[str] = Field(None, description="New contact number")

    @classmethod
    def as_form_base(
        cls,
        email: Optional[str] = Form(None),
        name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        birthdate: Optional[str] = Form(None),
        country_id: Optional[int] = Form(None),
        document_number: Optional[str] = Form(None),
        gender_id: Optional[int] = Form(None),
        contact_number: Optional[str] = Form(None),
    ):
        return cls(
            email=email, name=name, last_name=last_name, birthdate=birthdate,
            country_id=country_id, document_number=document_number,
            gender_id=gender_id, contact_number=contact_number
        )


class PaginatedAthletesResponse(BaseModel):
    """Paginated response for athlete lists."""
    items: List[AthleteBasicData]
    pagination: pagination_info_schema.PaginationInfo


class AthleteResponse(AthleteId):
    """Response model for athlete operations."""
    status: Literal[ResultEnum.SUCCESS, ResultEnum.FAILURE]
