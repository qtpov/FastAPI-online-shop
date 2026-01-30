from pydantic import BaseModel
from app.schemas.product import ProductRead

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: ProductRead | None = None

    model_config = {"from_attributes": True}


class CartRead(BaseModel):
    id: int
    items: list[CartItemRead]

    model_config = {"from_attributes": True}