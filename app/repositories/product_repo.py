from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product

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
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update_product(self, product: Product, data: dict) -> Product | None:
        if not product:
            return None
        # только существующие поля будут обновлены
        valid_fields = {column.name for column in Product.__table__.columns}
        for key, value in data.items():
            if key in valid_fields:
                setattr(product, key, value)
        try:
            await self.db.commit()
            await self.db.refresh(product)
            return product
        except Exception:
            await self.db.rollback()
            return None
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