from pydantic import BaseModel, Field
import datetime


class BGRequestCreateSchema(BaseModel):
    purchase_number: str
    inn: int
    amount: int
    days: int
    bg_type: int
    last_quarter: str = Field(default='profit')
    lesion_amount: int = Field(default=0)
    specifics_of_work: int


class BankInfo(BaseModel):
    name: str
    max_days: int

class BGRequestDetailInfoSchema(BaseModel):
    purchase_number: str
    company_name: str
    amount: int
    inn: int
    banks_ids: list


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
