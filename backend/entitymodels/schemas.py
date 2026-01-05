from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str

# 这些都是一个个的json
class LoginResponse(BaseModel):
    status: int
    message: str
    token: str


class TokenData(BaseModel):
    username: Optional[str] = None
    usertype: Optional[str] = None


# class UserBase(BaseModel):
#     username: str
#     email: str
#     usertype: str
#     status: bool
#
#
# class User(UserBase):
#     id: int
#
#     class Config:
#         from_attributes = True


class JWTPayload(BaseModel):
    user_id: int
    username: str
    usertype: int
    exp: int