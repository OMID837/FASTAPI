from fastapi import APIRouter, Body, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user
from db.engine import get_db
from db.models import User
from schemas._input import RegisterUser
from utilitis.secret import pwd_context
from utilitis.setings import generate_activation_token, verify_activation_token, executor, send_email_thread

router = APIRouter(
    prefix='/users',
    tags=['users']
)


# @router.post('/register')
# def register(data: RegisterUser = Body(), db: Session = Depends(get_db), request: Request = None):
#     hash_password = pwd_context.hash(data.password)
#     create_user = User(
#         username=data.username,
#         password=hash_password,
#         is_active=False
#     )
#     db.add(create_user)
#     db.commit()
#     db.refresh(create_user)
#     token = generate_activation_token(create_user.username)
#     activation_link = request.url_for("activate_account", token=token)
#
#     # ارسال ایمیل
#     subject = "Activate your account"
#     message = f"Hi,\nPlease click the link to activate your account:\n{activation_link}"
#     send_email(subject, create_user.username, message)
#
#     return {"message": "Check your email to activate your account."}
#     # return {"id": create_user.id, "username": create_user.username}

@router.post('/register')
def register(data: RegisterUser = Body(), db: Session = Depends(get_db), request: Request = None):
    # هش پسورد و ایجاد کاربر
    hash_password = pwd_context.hash(data.password)
    create_user = User(
        username=data.username,
        password=hash_password,
        is_active=False
    )
    db.add(create_user)
    db.commit()
    db.refresh(create_user)

    # ساخت توکن و لینک فعال‌سازی
    token = generate_activation_token(create_user.username)
    activation_link = request.url_for("activate_account", token=token)

    # متن ایمیل
    subject = "Activate your account"
    message = f"Hi,\nPlease click the link to activate your account:\n{activation_link}"

    # اضافه کردن ارسال ایمیل به thread جدا
    executor.submit(send_email_thread, subject, create_user.username, message)

    return {"message": "Check your email to activate your account."}


@router.get("/activate/{token}")
def activate_account(token: str, db: Session = Depends(get_db)):
    email = verify_activation_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.username == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        return {"message": "Account already activated"}

    user.is_active = True
    db.commit()
    return {"message": "Account activated successfully"}


@router.get('/user-get-profile/{username}')
def user_get_profile(username: str, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.username == username).first()
    return query


@router.put('/upadate-user-profile/{username}')
def upadate_username(username: str, newusername: str, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.username == username).first()
    query.username = newusername
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


@router.post('/delete-user/{username}')
def delete_user(username: str, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.username == username).first()
    db.delete(query)
    db.commit()
    return {'message': 'user deleted'}


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    # 🔒 این endpoint امن شده و Swagger قفل می‌زند
    return {"id": current_user.id, "username": current_user.username}
