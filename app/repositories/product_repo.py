from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.models.order import OrderItem
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
class ProductRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product_by_id(self, product_id: int) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    
    async def list_active_products(self) -> list[Product]:
        result = await self.db.execute(select(Product).where(Product.is_active == True))
        return result.scalars().all()

    async def create_product(self, product: Product) -> Product:
        self.db.add(product)
        try:
            await self.db.commit()
            await self.db.refresh(product)
            return product
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Product with this name already exists"
            )


    async def update_product(self, product: Product) -> Product:
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def is_used_in_orders(self, product_id: int) -> bool:
        stmt = select(
            exists().where(OrderItem.product_id == product_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def delete_product(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()

    async def search_products(self, query: str) -> list[Product]:
        result = await self.db.execute(
            select(Product).where(Product.is_active == True).where(
                Product.name.ilike(f"%{query}%") | Product.description.ilike(f"%{query}%")
            )
        )
        return result.scalars().all()