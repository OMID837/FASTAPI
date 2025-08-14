from db.engine import engine
from db.engine import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str | None] = mapped_column(
        String(50), unique=True,
        default=None,
        nullable=True
    )
    password: Mapped[int] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


Base.metadata.create_all(bind=engine)
