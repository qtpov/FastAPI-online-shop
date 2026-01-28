from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    image_url: str | None = None
    class Config:
        from_attributes = True

class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    is_active: bool
    image_url: str | None

    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None
    is_active: bool | None = None
    image_url: str | None = None
