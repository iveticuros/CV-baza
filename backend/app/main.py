from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import auth, users, students, fakulteti

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CV Baza API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)
app.include_router(fakulteti.router)

@app.get("/")
def root():
    return {"message": "CV Baza API", "version": "1.0.0"}
