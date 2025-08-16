from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import requests, json
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.carts import Cart, CartItem
from db.engine import get_db
from db.orders import Order, OrderItem
from db.users import User
from schemas.orders import OrderSchema

# فرض می‌کنیم این تابع CurrentUser میده

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/from-cart", response_model=OrderSchema)
def create_order_from_cart(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cart = db.query(Cart).join(CartItem).filter(CartItem.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_total = sum(item.product.price * item.quantity for item in cart.items)
    order = Order(
        user_id=current_user.id,
        first_name=current_user.username,  # یا هر فیلد دلخواه
        order_total=order_total
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            user_id=current_user.id,
            product_id=item.product.id,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
        )
        db.add(order_item)
        db.delete(item)  # پاک کردن آیتم از سبد

    db.commit()
    db.refresh(order)
    return order


MERCHANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
START_URL = "https://sandbox.zarinpal.com/pg/StartPay/"
REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

CALLBACK_URL = "http://127.0.0.1:8000/payment/verify"


@router.get("/start/{order_id}")
def start_payment(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    data = {
        "merchant_id": MERCHANT_ID,
        "amount": order.order_total,
        "callback_url": CALLBACK_URL,
        "description": f"Payment for order #{order.id}",
        "metadata": {"email": current_user.username, "mobile": current_user.username}
    }

    response = requests.post(url=REQUEST_URL, headers=HEADERS, json=data)

    if response.status_code == 200:
        resp_data = response.json()["data"]
        authority = resp_data["authority"]
        order.authority = authority
        db.commit()
        payment_url = f"{START_URL}{authority}/"
        return {"payment_url": payment_url}

    raise HTTPException(status_code=400, detail="پرداخت انجام نشد، لطفاً مجدداً تلاش کنید.")


VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"


@router.get("/verify")
def verify_payment(Authority: str, Status: str, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    if Status != "OK":
        raise HTTPException(status_code=400, detail="پرداخت ناموفق بود")

    order = db.query(Order).filter(Order.authority == Authority, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    data = {"merchant_id": MERCHANT_ID, "amount": order.order_total, "authority": Authority}
    response = requests.post(url=VERIFY_URL, headers=HEADERS, json=data)
    resp_data = response.json()["data"]
    code = resp_data.get("code")

    if code == 100:
        order.is_pay = True
        db.commit()
        return {"message": f"پرداخت موفق، RefID: {resp_data.get('ref_id')}"}

    raise HTTPException(status_code=400, detail="پرداخت ناموفق بود")
