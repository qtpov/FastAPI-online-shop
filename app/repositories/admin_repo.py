from app.repositories.user_repo import UserRepo
from app.repositories.order_repo import OrderRepo
from app.repositories.product_repo import ProductRepo
from app.models.product import Product
from app.schemas.product import ProductCreate
from fastapi import HTTPException

from app.models.user import User

class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def get_user(self, user_id: int) -> User | None:
        return await self.repo.get_by_id(user_id)

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.repo.list_users(skip, limit)

    async def create_user(self, email: str, password_hash: str, role: str = "user") -> User:
        user = User(email=email, hashed_password=password_hash, role=role)
        return await self.repo.create_user(user)

    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if user:
            await self.repo.delete_user(user)

    async def promote_user_to_admin(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if user:
            user.role = "admin"
            await self.repo.update_user(user)

    async def demote_admin_to_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if user:
            user.role = "user"
            await self.repo.update_user(user)

class OrderService:
    def __init__(self, repo: OrderRepo):
        self.repo = repo

    async def get_orders_by_user(self, user_id: int):
        return await self.repo.list_orders_by_user(user_id)

    async def change_order_status(self, order_id: int, new_status: str):
        order = await self.repo.get_order_by_id(order_id)
        if not order:
            return None
        order.status = new_status
        return await self.repo.update_order(order)

    

class ProductService:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    async def list_products(self):
        return await self.repo.list_active_products()

    async def create_product(self, name: str, description: str, price: float, quantity: int):
        product = Product(name=name, description=description, price=price, quantity=quantity)
        return await self.repo.create_product(product)

    async def update_product(self, product_id: int, data: ProductCreate):
        product = await self.repo.get_product_by_id(product_id)
        if not product:
            return None

        for field, value in data.dict(exclude_unset=True).items():
            setattr(product, field, value)


        return await self.repo.update_product(product)
    

    async def delete_product(self, product_id: int):
        product = await self.repo.get_product_by_id(product_id)
        if not product:
            return None

        if await self.repo.is_used_in_orders(product_id):
            raise HTTPException(
                status_code=400,
                detail="Product is used in orders and cannot be deleted"
            )

        await self.repo.delete_product(product)
        return True
    