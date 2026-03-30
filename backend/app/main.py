import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import settings
from .errors import register_exception_handlers
from .rate_limit import limiter
from .request_context import client_ip_ctx, request_id_ctx
from .routes import admin, auth, company, fakulteti, studijski_programi, students, tehnologije


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="CV Baza API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
register_exception_handlers(app)


@app.middleware("http")
async def add_request_id_and_headers(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token_rid = request_id_ctx.set(rid)
    forwarded = request.headers.get("X-Forwarded-For")
    ip = (forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None))
    token_ip = client_ip_ctx.set(ip)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    request_id_ctx.reset(token_rid)
    client_ip_ctx.reset(token_ip)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/privacy-policy")
def privacy_policy():
    return {
        "title": "Politika privatnosti (ZZPL)",
        "summary": (
            "Prikupljamo podatke neophodne za matching studenata i kompanija. Imate pravo na pristup, "
            "ispravku i brisanje podataka. Obrada se vodi evidencija u sistemu. Kontakt: administrator domene."
        ),
    }


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(company.router)
app.include_router(students.router)
app.include_router(fakulteti.router)
app.include_router(studijski_programi.router)
app.include_router(tehnologije.router)
