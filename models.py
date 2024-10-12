from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: date

class ItemResponse(BaseModel):
    id: str
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: date
    insert_date: datetime

class ItemUpdate(BaseModel):
    name: Optional[str]
    item_name: Optional[str]
    quantity: Optional[int]
    expiry_date: Optional[date]

class ClockInCreate(BaseModel):
    email: EmailStr
    location: str

class ClockInUpdate(BaseModel):
    location: Optional[str]
