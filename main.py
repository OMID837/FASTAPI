from fastapi import FastAPI, Body
from fastapi_pagination import add_pagination
from pydantic import BaseModel

from routers.users import router as user_router
from auth.authentication import router as authentication
from routers.products import router as products
from routers.carts import router as carts
from routers.orders import router as orders

app = FastAPI()

app.include_router(user_router)
app.include_router(authentication)
app.include_router(products)
app.include_router(carts)
app.include_router(orders)


add_pagination(app)