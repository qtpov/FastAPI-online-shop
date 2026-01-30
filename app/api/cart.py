from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.repositories.cart_repo import CartRepo
from app.repositories.product_repo import ProductRepo
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartRead
from app.models.cart import CartItem
from app.models.product import Product

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=CartRead)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    repo = CartRepo(db)
    cart = await repo.get_or_create_cart(user_id)

    # подставляем продукт в каждый элемент
    for item in cart.items:
        if hasattr(item, "product_id") and not getattr(item, "product", None):
            product = await db.get(Product, item.product_id)
            item.product = product

    return cart


@router.post("/items")
async def add_item(
    item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    cart_repo = CartRepo(db)
    product_repo = ProductRepo(db)

    product = await product_repo.get_product_by_id(item.product_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Product not available")

    if item.quantity > product.quantity:
        raise HTTPException(409, "Not enough stock")

    cart = await cart_repo.get_or_create_cart(user_id)
    await cart_repo.add_item(cart, product, item.quantity)
    return cart


@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    cart_repo = CartRepo(db)
    cart = await cart_repo.get_or_create_cart(user_id)
    
    item = await db.get(CartItem, item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(404, "Item not found")
    
    if data.quantity <= 0:
        await db.delete(item)
        await db.commit()
        return {"detail": "Item removed"}
    
    await cart_repo.update_item(item, data.quantity)
    await db.refresh(item)
    return item



@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    cart_repo = CartRepo(db)
    cart = await cart_repo.get_or_create_cart(user_id)
    
    success = await cart_repo.remove_item(cart.id, item_id)
    if not success:
        raise HTTPException(404, "Item not found")
    return {"detail": "Item removed"}


@router.delete("/")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    cart_repo = CartRepo(db)
    cart = await cart_repo.get_or_create_cart(user_id)
    
    await cart_repo.clear_cart(cart.id)
    return {"detail": "Cart cleared"}
