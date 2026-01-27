from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int

class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    is_active: bool

    class Config:
        orm_mode = True