from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    code: str
    is_active: bool = True
    auth_count: int
    user_id: str


class UpdateToken(BaseModel):
    code: Optional[str] = None
    is_active: Optional[bool] = None
    auth_count: Optional[int] = None
    user_id: Optional[str] = None
