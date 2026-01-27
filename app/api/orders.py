from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.core.database import get_db
from app.repositories.cart_repo import CartRepo
from app.repositories.order_repo import OrderRepo
from app.repositories.product_repo import ProductRepo
from app.schemas.order import OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderRead)
async def create_order(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    
    cart_repo = CartRepo(db)
    product_repo = ProductRepo(db)
    order_repo = OrderRepo(db)
    
    cart = await cart_repo.get_or_create_cart(user_id)
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Создаём заказ из корзины
    order = await order_repo.create_order_from_cart(user_id, cart)
    
    # Обновляем остатки на складе
    for item in order.items:
        product = await product_repo.get_product_by_id(item.product_id)
    
    return order

@router.get("/", response_model=list[OrderRead])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    order_repo = OrderRepo(db)

    orders = await order_repo.list_orders_by_user(user_id)
    return orders

@router.post('/{order_id}/pay', response_model=OrderRead)
async def pay_order( 
    order_id: int, db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)):

    user_id = current_user["user_id"]
    order_repo = OrderRepo(db)

    order = await order_repo.pay_order(order_id, user_id)
    return order

@router.post('/{order_id}/cancel', response_model=OrderRead)
async def cancel_order( 
    order_id: int, db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)):

    user_id = current_user["user_id"]
    order_repo = OrderRepo(db)

    order = await order_repo.cancel_order(order_id, user_id)
    return order