from enum import Enum
from typing import Optional

from google.cloud.firestore_v1 import DocumentReference
from pydantic import BaseModel, EmailStr, Field


class UserType(str, Enum):
    """
    Enumeration of possible user
    """
    PLAYER = 'player'
    COACH = 'coach'
    ADMIN = 'admin'


class UserProfile(BaseModel):
    """
    General user profile for user admin type
    """
    id: Optional[str] = None
    user_type: UserType = Field(default=UserType.ADMIN, alias='userType')
    first_name: str = Field(alias='firstName')
    middle_name: Optional[str] = Field(default=None, alias='middleName')
    last_name: str = Field(alias='lastName')
    birth_date: str = Field(alias='birthday')
    club_id: str = Field(alias='clubID')
    phone: str
    email: EmailStr
    info: Optional[str] = None
    token: Optional[str] = None

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class UpdateUserProfile(BaseModel):
    first_name: Optional[str] = Field(default=None, alias='firstName')
    middle_name: Optional[str] = Field(default=None, alias='middleName')
    last_name: Optional[str] = Field(default=None, alias='lastName')
    birth_date: Optional[str] = Field(default=None, alias='birthday')
    phone: Optional[str] = None
    info: Optional[str] = None



class Club(BaseModel):
    club_name: str = Field(alias='name')
    motto: Optional[str] = None
