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
    
    # Берём корзину
    cart = await cart_repo.get_or_create_cart(user_id)
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Проверяем наличие товаров на складе
    for item in cart.items:
        product = await product_repo.get_product_by_id(item.product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not available")
        if item.quantity > product.quantity:
            raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
    
    # Создаём заказ из корзины
    order = await order_repo.create_order_from_cart(user_id, cart)
    
    # Обновляем остатки на складе
    for item in order.items:
        product = await product_repo.get_product_by_id(item.product_id)
        product.quantity -= item.quantity
    
    # Чистим корзину
    await cart_repo.clear_cart(cart.id)
    
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