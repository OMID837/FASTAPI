from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProductSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class OrderItemSchema(BaseModel):
    id: int
    product: ProductSchema
    quantity: int
    product_price: float

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address1: Optional[str]
    country: Optional[str]
    city: Optional[str]
    order_total: Optional[float]
    is_pay: bool
    updated_at: datetime
    items: List[OrderItemSchema] = []

    class Config:
        from_attributes = True


class WalletSchema(BaseModel):
    user_id: int
    balance: float

    class Config:
        from_attributes = True


class TransactionSchema(BaseModel):
    id: int
    user_id: int
    authority: Optional[str]
    amount: float
    transaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True
