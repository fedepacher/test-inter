from datetime import datetime
from pydantic import BaseModel, Field


class ProfessionalRolesBase(BaseModel):
    id: int
    name: str = Field(..., max_length=30, unique=True)

    class Config:
        from_attributes = True


class ProfessionalRoles(ProfessionalRolesBase):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
