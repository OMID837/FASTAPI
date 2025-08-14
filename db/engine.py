from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# آدرس دیتابیس (اینجا SQLite برای تست گذاشتم)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
# برای PostgreSQL:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# برای SQLite نیاز به connect_args داریم
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # فقط برای SQLite
)

# ساخت Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base برای ساخت مدل‌ها
Base = declarative_base()

# Dependency برای FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
