from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate
from db.engine import get_db
from db.products import Product, Category
from schemas.products import CategorySchema, CategorySchemaCreate, ProductCreateSchema

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=Page[ProductCreateSchema])
def list_products(
        db: Session = Depends(get_db),
        category_id: int | None = None,  # فیلتر بر اساس دسته‌بندی
        in_stock: bool | None = None
):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if in_stock is not None:
        query = query.filter(Product.in_stock == in_stock)

    return paginate(query.all())


@router.post("/create-product")
def create_product(data: ProductCreateSchema = Body(), db: Session = Depends(get_db)):
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        in_stock=data.in_stock,
        category_id=data.category_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.post("/create-category", response_model=CategorySchemaCreate)
def create_category(data: CategorySchemaCreate = Body(), db: Session = Depends(get_db)):
    cat = Category(
        name=data.name,
        is_active=data.is_active,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
