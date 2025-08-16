from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProductSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class CartItemSchema(BaseModel):
    id: int
    product: ProductSchema
    quantity: int
    is_active: bool
    sub_total: float

    class Config:
        from_attributes = True


class CartSchema(BaseModel):
    id: int
    date_added: datetime
    items: List[CartItemSchema] = []

    class Config:
        from_attributes = True
