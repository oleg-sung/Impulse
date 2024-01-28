from typing import Optional

from pydantic import BaseModel, Field

from backend.users.schema import UserType


class Token(BaseModel):
    """General token schema"""
    code: str = Field(default='IsAdminToken')
    is_active: bool = Field(default=True, alias='isActive')
    auth_count: int = Field(default=0, alias='authCount')
    user_type: UserType = Field(default=UserType.ADMIN, alias='userType')
    user_id: str = Field(alias='userCreatedID')
    club_id: str = Field(alias='clubID')

    class Config:
        populate_by_name = True


class UpdateToken(BaseModel):
    """Token schema for changing token info"""
    code: Optional[str] = None
    is_active: Optional[bool] = Field(alias='isActive')

    class Config:
        populate_by_name = True
