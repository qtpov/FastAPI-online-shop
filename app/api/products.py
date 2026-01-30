from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product_repo import ProductRepo
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead
from app.core.database import get_db
from app.api.deps import get_admin_user
from fastapi import Query

router = APIRouter(
    prefix="/products", tags=["products"]
)

@router.get("/", response_model=list[ProductRead])
async def list_products(q: str = None, db: AsyncSession = Depends(get_db)):
    repo = ProductRepo(db)
    if q:
        products = await repo.search_products(q)
    else:
        products = await repo.list_active_products()
    return products

@router.get("/search", response_model=list[ProductRead])
async def search_products(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    if not q:
        return []
    repo = ProductRepo(db)
    products = await repo.search_products(q)
    return products

@router.get("/{id}", response_model=ProductRead)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    repo = ProductRepo(db)
    product = await repo.get_product_by_id(id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

@router.post("/", response_model=ProductRead, dependencies=[Depends(get_admin_user)])
async def create_product(product_in: ProductCreate, db: AsyncSession = Depends(get_db),
            admin: dict = Depends(get_admin_user)):
    repo = ProductRepo(db)
    product = Product(**product_in.dict())
    return await repo.create_product(product)

@router.put("/{id}", response_model=ProductRead, dependencies=[Depends(get_admin_user)])
async def update_product(id: int, product_in: ProductCreate, db: AsyncSession = Depends(get_db),
                         admin: dict = Depends(get_admin_user)):
    repo = ProductRepo(db)
    product = await repo.get_product_by_id(id)
    if not product:
        raise HTTPException(404, "Product not found")
    return await repo.update_product(product, product_in.dict())

@router.delete("/{id}", dependencies=[Depends(get_admin_user)])
async def delete_product(id: int, db: AsyncSession = Depends(get_db),
                         admin: dict = Depends(get_admin_user)):
    repo = ProductRepo(db)
    product = await repo.get_product_by_id(id)
    if not product:
        raise HTTPException(404, "Product not found")
    await repo.delete_product(product)
    return {"detail": "Product deleted"}