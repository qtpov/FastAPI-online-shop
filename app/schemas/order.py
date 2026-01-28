from pydantic import BaseModel, computed_field
from app.schemas.product import ProductRead
from datetime import datetime
from enum import Enum

class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductRead

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: int
    user_id: int
    status: str
    items: list[OrderItemRead]
    
    model_config = {"from_attributes": True}

    @computed_field
    @property
    def total_price(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

class OrderHistoryRead(BaseModel):
    status: str
    changed_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class OrderStatusUpdate(str, Enum):
    created = "created"
    paid = "paid"
    shipped = "shipped"
    canceled = "canceled"
