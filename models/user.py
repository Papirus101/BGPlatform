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
    email: EmailStr
    inn: int = Field(lt=9999999999)
    name_organization: str | None
    fio: str
    phone: str
    user_type: UserTypes


class LoginResponseSchema(BaseModel):
    user_info: UserInfoSchema
    Authorization: str

class UserAllInfoSchema(UserInfoSchema):
    photo: str | None


class UserRegisterSchema(UserInfoSchema):
    password: str

    @validator('phone')
    def phone_validator(cls, v):
        regex = r"^(\+)7[0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError('Phone number invalid')
        return v


class UserUpdateSchema(BaseModel):
    inn: int | None
    fio: str | None
    phone: str | None
    email: EmailStr | None
    password: str | None

    @validator('phone')
    def phone_validator(cls, v):
        if v is None:
            return v
        regex = r"^(\+)7[0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError('Phone number invalid')
        return v


class ReasonsDeletedShema(str, Enum):
    bank_requirement = 'bank'
    license = 'license'
    conflict = 'conflict'
    another = 'another'


class UserDeleteSchema(BaseModel):
    reason_deleted: ReasonsDeletedShema
    delete_text: str | None
