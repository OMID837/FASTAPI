from pydantic import BaseModel


class RegisterUser(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    id: int
    username: str | None
    is_active: bool

    class Config:
        from_attributes = True  # 👈 بجای orm_mode
        
    # class Config:   paydandic v1
    #     orm_mode = True  # 👈 خیلی مهم برای کار با SQLAlchemy

