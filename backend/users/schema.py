from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserType(str, Enum):
    PLAYER = 'player'
    COACH = 'coach'
    ADMIN = 'admin'


class UserProfile(BaseModel):
    id: Optional[str] = None
    user_type: UserType = UserType.ADMIN
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    birth_date: str
    phone: str
    email: EmailStr
    info: Optional[str] = None
    token: Optional[str] = None

    class Config:
        use_enum_values = True
