from pydantic import BaseModel


class CategorySchema(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class CategorySchemaCreate(BaseModel):
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class ProductCreateSchema(BaseModel):
    name: str
    description: str | None
    price: float
    in_stock: bool
    category_id: int  # فقط آیدی دسته‌بندی

    class Config:
        from_attributes = True
