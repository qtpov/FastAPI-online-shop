from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_admin_user
from app.core.database import get_db
from app.repositories.admin_repo import UserService
from app.repositories.admin_repo import OrderService
from app.repositories.admin_repo import ProductService
from app.repositories.product_repo import ProductRepo
from app.repositories.user_repo import UserRepo
from app.repositories.order_repo import OrderRepo
from app.schemas.user import UserRead, UserCreate
from app.schemas.product import ProductCreate, ProductRead
from app.schemas.order import OrderRead, OrderStatusUpdate
from app.core.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[UserRead])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                     admin_user: dict = Depends(get_admin_user)):
    service = UserService(UserRepo(db))
    return await service.list_users(skip, limit)

@router.post("/users", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db),
                      admin_user: dict = Depends(get_admin_user)):
    service = UserService(UserRepo(db))
    return await service.create_user(user.email, hash_password(user.password), user.role)

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db),
                      admin_user: dict = Depends(get_admin_user)):
    service = UserService(UserRepo(db))
    await service.delete_user(user_id)
    return {"detail": "User deleted"}

@router.post("/users/{user_id}/promote")
async def promote_user_to_admin(user_id: int, db: AsyncSession = Depends(get_db),
                                admin_user: dict = Depends(get_admin_user)):
    service = UserService(UserRepo(db))
    await service.promote_user_to_admin(user_id)
    return {"detail": "User promoted to admin"}

@router.post("/users/{user_id}/demote")
async def demote_admin_to_user(user_id: int, db: AsyncSession = Depends(get_db),
                               admin_user: dict = Depends(get_admin_user)):
    service = UserService(UserRepo(db))
    await service.demote_admin_to_user(user_id)
    return {"detail": "Admin demoted to user"}

@router.get("/users/{user_id}/orders", response_model=list[OrderRead])
async def get_orders_by_user(user_id: int, db: AsyncSession = Depends(get_db),
                             admin_user: dict = Depends(get_admin_user)):
    order_service = OrderService(OrderRepo(db))
    return await order_service.get_orders_by_user(user_id)

@router.put("/orders/{order_id}/status")
async def change_order_status(order_id: int, new_status: OrderStatusUpdate, db: AsyncSession = Depends(get_db),
                              admin_user: dict = Depends(get_admin_user)):
    order_service = OrderService(OrderRepo(db))
    order = await order_service.change_order_status(order_id, new_status.status)
    if order:
        return order
    raise HTTPException(status_code=404, detail="Order not found")

@router.get("/products", response_model=list[ProductRead])
async def list_products( db: AsyncSession = Depends(get_db),
                        admin_user: dict = Depends(get_admin_user)):
    service = ProductService(ProductRepo(db))
    return await service.list_products()

@router.post("/products", response_model=ProductRead)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_admin_user),
):
    service = ProductService(ProductRepo(db))
    return await service.create_product(
        data.name,
        data.description,
        data.price,
        data.quantity,
        data.image_url,
    )

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_admin_user),
):
    service = ProductService(ProductRepo(db))
    result = await service.delete_product(product_id)

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"status": "deleted"}

@router.put("/products/{product_id}",response_model=ProductRead)
async def update_product(
    product_id: int, product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_admin_user),
):
    service = ProductService(ProductRepo(db))
    product = await service.update_product(product_id, product_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


