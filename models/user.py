from pydantic import BaseModel, Field, EmailStr, validator

from enum import Enum, IntEnum

import re


class UserTypes(str, Enum):
    client = 'client'
    agent = 'agent'
    bank = 'bank'


class UserLoginSchema(BaseModel):
    login: str = Field(default=None)
    password: str


class UserRegisterSchema(BaseModel):
    login: str = Field(default=None)
    email: EmailStr = Field(default=None)
    inn: int = Field(default=None, max_length=10)
    fio: str = Field(default=None)
    phone: str
    password: str = Field(default=None)
    user_type: UserTypes = UserTypes.client

    @validator('phone')
    def phone_validator(self, v):
        regex = r"^(\+)7[0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError('Phone number invalid')
        return v
