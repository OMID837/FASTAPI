from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Body
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from auth.auth_form import CustomOAuth2PasswordRequestForm
from auth.oauth2 import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, SECRET_KEY, ALGORITHM
from db.users import User
from db.engine import get_db
from utilitis.secret import pwd_context
from auth import oauth2
from fastapi import Response

router = APIRouter(
    prefix="/authentication",
    tags=["authentication"]
)


@router.post("/token")
def login(response: Response, form_data: CustomOAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username, User.is_active == True).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = oauth2.create_access_token(data={"sub": user.username})
    refresh_token = oauth2.create_refresh_token(data={"sub": user.username})
    # ست کردن Refresh Token در HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 روز
        samesite="strict",
        path="/",

    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_access_token(
        # از کوکی بگیر (واقعیِ ذخیره‌شده)
        refresh_token_cookie: str = Cookie(None, alias="refresh_token", include_in_schema=False),
        # از بدنه درخواست بگیر (اون چیزی که کاربر/کلاینت می‌فرسته برای مقایسه)
        refresh_token_input: str = Body(..., embed=True, description="refresh_token"),
        db: Session = Depends(get_db),
):
    # 1) وجود کوکی
    if not refresh_token_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token in cookies")

    # 2) مقایسه ورودی با کوکی
    if refresh_token_cookie != refresh_token_input:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch")

    # 3) وریفای امضا و انقضا
    try:
        payload = jwt.decode(refresh_token_cookie, oauth2.SECRET_KEY, algorithms=[oauth2.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    # 4) وجود کاربر
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # 5) ساخت Access جدید
    new_access = oauth2.create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token", path="/")
    return {"detail": "Logged out"}
