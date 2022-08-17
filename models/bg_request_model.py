from pydantic import BaseModel, Field
import datetime


class BGRequestCreateSchema(BaseModel):
    purchase_number: str
    inn: int
    amount: int
    days: int
    bg_type_id: int
    last_quarter: str = Field(default='profit')
    lesion_amount: int = Field(default=0)
    specifics_of_work_id: int
    is_ready: bool = Field(default=False)


class BankInfo(BaseModel):
    bank_id: int | None
    bank_name: str | None
    bank_stavka: int | None
    brokers_terms: int | None

class BGRequestDetailInfoSchema(BaseModel):
    id: int
    inn: int
    purchase_number: str
    purchase_name: str | None
    amount: int
    days: int
    banks: list[BankInfo]

class BGTypesSpecificsSchema(BaseModel):
    id: int
    name: str
    description: str


class BGTypesSpicificsListShema(BaseModel):
    data: list[BGTypesSpecificsSchema]


class BGRequestListInfoSchema(BaseModel):
    id: int
    purchase_number: str
    name_organization: str | None
    amount: int
    days: int
    is_ready: bool


class BGRequestsListSchema(BaseModel):
    requests: list[BGRequestListInfoSchema]


class BGRequestAuctionStart(BaseModel):
    request_id: int
    date_finish: datetime.datetime
    all_brokers: bool
    brokers: list[int] | None
