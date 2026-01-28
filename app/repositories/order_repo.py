from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.order import Order, OrderItem, OrderHistory
from app.models.cart import CartItem
from app.repositories.product_repo import ProductRepo
from datetime import datetime


class OrderRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order_from_cart(self, user_id: int, cart):
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        product_repo = ProductRepo(self.db)

        # создаём заказ
        order = Order(user_id=user_id, status="pending")
        self.db.add(order)
        await self.db.flush()  # чтобы получить order.id для OrderItem

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

            product.quantity -= cart_item.quantity

        # чистим корзину
        await self.db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))

        await self.db.flush()  # отправляем все изменения в базу, но не коммитим

        # запись в историю
        history = OrderHistory(order_id=order.id, status=order.status, user_id=user_id)
        self.db.add(history)

        # перечитываем заказ с items и product
        stmt = (
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

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


    async def pay_order(self, order_id: int, user_id: int):
        async with self.db.begin():  # транзакция
            stmt = select(Order).where(Order.id == order_id, Order.user_id == user_id)
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if order.status != "pending":
                raise HTTPException(status_code=409, detail="Order cannot be paid")

            order.status = "paid"

            # запись в историю
            history = OrderHistory(order_id=order.id, status=order.status, user_id=user_id)
            self.db.add(history)

        # перечитываем заказ 
        stmt = (
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()


    async def cancel_order(self, order_id: int, user_id: int):
        async with self.db.begin():  # транзакция
            stmt = select(Order).where(Order.id == order_id, Order.user_id == user_id).options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if order.status != "pending":
                raise HTTPException(status_code=409, detail="Order cannot be cancelled")

            # возвращаем товары на склад
            for item in order.items:
                item.product.quantity += item.quantity

            order.status = "cancelled"

            # запись в историю
            history = OrderHistory(order_id=order.id, status=order.status, user_id=user_id)
            self.db.add(history)

        stmt = (
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_order_history(self, order_id: int, user_id: int):
        stmt = select(OrderHistory).where(OrderHistory.order_id == order_id, OrderHistory.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_order_by_id(self, order_id: int):
        stmt = select(Order).where(Order.id == order_id).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_order(self, order: Order):
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order