from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.repositories.product_repo import ProductRepo


class OrderRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order_from_cart(self, user_id: int, cart):
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        product_repo = ProductRepo(self.db)

        # 1. Создаём заказ
        order = Order(user_id=user_id, status="pending")
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)

        # 2. Создаём OrderItems и уменьшаем склад
        for cart_item in cart.items:
            product = await product_repo.get_product_by_id(cart_item.product_id)
            if not product or not product.is_active:
                raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not available")
            if cart_item.quantity > product.quantity:
                raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=cart_item.quantity,
                price=product.price
            )
            self.db.add(order_item)

            # уменьшаем количество на складе
            product.quantity -= cart_item.quantity

        # 3. Чистим корзину
        await self.db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))

        # 4. Финальный коммит
        await self.db.commit()

        # 5. Загружаем order с items и product для сериализации
        stmt = (
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
        )
        result = await self.db.execute(stmt)
        order = result.scalar_one()

        return order

    async def list_orders_by_user(self, user_id: int):
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
