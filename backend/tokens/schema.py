from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """General token schema"""
    code: str
    is_active: bool = True
    auth_count: int
    user_id: str


class UpdateToken(BaseModel):
    """Token schema for changing token info"""
    code: Optional[str] = None
    is_active: Optional[bool] = None
    auth_count: Optional[int] = None
    user_id: Optional[str] = None
