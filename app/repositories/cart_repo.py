from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from app.models.cart import Cart, CartItem

class CartRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(self, user_id: int):
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product)
            )
        )
        result = await self.db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)

        return cart

    async def get_item(self, cart_id: int, product_id: int):
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()

    async def add_item(self, cart: Cart, product, quantity: int):
        item = await self.get_item(cart.id, product.id)

        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price,  
            )
            self.db.add(item)

        await self.db.commit()
        return item

    async def update_item(self, item: CartItem, quantity: int):
        item.quantity = quantity
        await self.db.commit()
        return item

    async def remove_item(self, cart_id: int, item_id: int):
        item = await self.db.get(CartItem, item_id)
        if item and item.cart_id == cart_id:
            await self.db.delete(item)
            await self.db.commit()
            return True
        return False

    async def clear_cart(self, cart_id: int):
        await self.db.execute(
            delete(CartItem).where(CartItem.cart_id == cart_id)
        )
        await self.db.commit()

    async def delete_item(self, item: CartItem):
        await self.db.delete(item)
        await self.db.commit()
