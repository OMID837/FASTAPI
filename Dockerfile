# از Python slim استفاده می‌کنیم (سبک‌تر از full)
FROM python:3.11-slim

# محیط کاری داخل کانتینر
WORKDIR /app

# نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# پورت پیش‌فرض uvicorn
EXPOSE 8000


