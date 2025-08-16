from sqlalchemy import ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from db.engine import Base
from db.products import Product  # فرض می‌کنیم مدل User داری
from db.users import User  # فرض می‌کنیم مدل User داری


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date_added: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items = relationship("CartItem", back_populates="cart")  # همه آیتم‌های سبد


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship(User)
    cart = relationship(Cart, back_populates="items")
    product = relationship(Product)

    # متد محاسبه زیرمجموعه
    @property
    def sub_total(self) -> float:
        return self.quantity * self.product.price
