FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py reset_presence && gunicorn core.asgi:application -k uvicorn.workers.UvicornWorker -w 3 -b 0.0.0.0:8000 --timeout 60 --access-logfile -"]

# -k uvicorn.workers.UvicornWorker - for websocket