from enum import Enum
from typing import Optional

from google.cloud.firestore_v1 import DocumentReference, FieldFilter
from pydantic import BaseModel, EmailStr, Field, model_validator

from backend.error import HttpError
from backend.firebase_db import club_model


class UserType(str, Enum):
    """
    Enumeration of possible user
    """
    PLAYER = 'player'
    COACH = 'coach'
    ADMIN = 'admin'


class UserProfileSchema(BaseModel):
    """
    General user profile for user admin type
    """
    user_type: UserType = Field(default=UserType.ADMIN, alias='userType')
    first_name: str = Field(alias='firstName')
    middle_name: Optional[str] = Field(default=None, alias='middleName')
    last_name: str = Field(alias='lastName')
    birth_date: str = Field(alias='birthday')
    club_id: str = Field(alias='clubID')
    phone: str
    email: EmailStr
    info: Optional[str] = None
    token: DocumentReference

    class Config:
        use_enum_values = True
        populate_by_name = True
        arbitrary_types_allowed = True


class UpdateUserProfileSchema(BaseModel):
    first_name: Optional[str] = Field(default=None, alias='firstName')
    last_name: Optional[str] = Field(default=None, alias='lastName')
    birth_date: Optional[str] = Field(default=None, alias='birthday')
    phone: Optional[str] = None
    info: Optional[str] = None


class ClubSchema(BaseModel):
    club_name: str = Field(alias='name')
    motto: Optional[str] = None

    @model_validator(mode='after')
    def check_club_name(self):
        result = club_model.where(filter=FieldFilter('name', '==', self.club_name)).get()
        if result:
            raise HttpError(400, 'Club name already exists')
        return self

    class Config:
        populate_by_name = True


class UpdateClubSchema(ClubSchema):
    image: Optional[str] = None
    club_name: Optional[str] = Field(default=None, alias='name')
