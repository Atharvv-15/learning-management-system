from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

#Create a Token payload schema
class TokenPayload(BaseModel):
    user_id: Optional[int] = None