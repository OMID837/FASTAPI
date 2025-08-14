from fastapi import FastAPI, Body
from pydantic import BaseModel

from routers.users import router as user_router
from auth.authentication import router as authentication

app = FastAPI()

app.include_router(user_router)
app.include_router(authentication)
