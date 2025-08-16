from fastapi import Form
from typing import Optional


class CustomOAuth2PasswordRequestForm:
    def __init__(
            self,
            username: str = Form(...),
            password: str = Form(...),
            email: Optional[str] = Form(None),  # 👈 فیلد جدید
    ):
        self.username = username
        self.password = password
        self.email = email
