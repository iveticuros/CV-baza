FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=builder /install /usr/local
RUN useradd -m -u 1000 appuser
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
RUN mkdir -p /app/data/cv_uploads && chown appuser:appuser /app/data/cv_uploads
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
