from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.engine import get_db
from db.users import User
from db.carts import Cart, CartItem
from db.products import Product
from schemas.carts import CartItemSchema

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/add-item/{product_id}")
def add_to_cart(
        product_id: int,
        quantity: int = 1,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # گرفتن سبد فعلی کاربر یا ساخت جدید
    cart = db.query(Cart).join(CartItem).filter(CartItem.user_id == current_user.id).first()
    if not cart:
        cart = Cart()
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # بررسی اینکه محصول قبلا تو سبد هست یا نه
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id,
        CartItem.user_id == current_user.id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            user_id=current_user.id,
            quantity=quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item
