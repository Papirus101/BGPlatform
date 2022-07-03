from pydantic import BaseModel, Field, EmailStr, validator

from enum import Enum

import re


class UserTypes(str, Enum):
    client = 'client'
    agent = 'agent'
    bank = 'bank'


class UserLoginSchema(BaseModel):
    login: str = Field(default=None)
    password: str


class UserInfoSchema(BaseModel):
    login: str
    email: str
    inn: int = Field(lt=9999999999)
    fio: str
    phone: str
    user_type: UserTypes


class UserAllInfoSchema(UserInfoSchema):
    image: str | None


class UserRegisterSchema(UserInfoSchema):
    password: str = Field()

    @validator('phone')
    def phone_validator(cls, v):
        regex = r"^(\+)7[0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError('Phone number invalid')
        return v
