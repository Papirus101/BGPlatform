from pydantic import BaseModel, Field


class NewBankCompanyTypes(BaseModel):
    id: int


class NewBank(BaseModel):
    name: str
    min_company_dates: int = Field(default=0)
    execution_lists_amount: int = Field(default=0)
    bg_system_name: str = Field(default=None)
    bg_system_link: str = Field(default=None)
    authorized_capital: int = Field(default=0)
    amount_debt_on_taxes_and_fees: int = Field(default=0)
    mass_address: bool = Field(default=True)
    rezident: bool = Field(default=True)
    percent_revenue: int = Field(default=0)
    rnp: bool = Field(default=True)
    min_guarante: int = Field(default=0)
    max_guarante: int = Field(default=2147483647)
    region: str = Field(default=None)
    bankrupt: bool = Field(default=True)
    stavka: int = Field(default=1)
    lesion_year_amount: int = Field(default=0)
    min_days: int = Field(default=0)
    max_days: int = Field(default=900)
    brokers_terms: int = Field(default=1)
    lesion_quarterly_amount: int = Field(default=0)
    manager_id: int | None = Field(default=None)
    company_type: list
    fz_types: list
    bg_types: list
