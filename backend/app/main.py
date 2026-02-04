from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from .database import engine, get_db
from .routes import users, books, borrows, dashboard
import os

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise Library Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
app.include_router(borrows.router, prefix="/api/borrows", tags=["Borrows"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Enterprise Library Management System API"}
