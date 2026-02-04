from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import models, schemas, database
from ..database import get_db
from .users import get_admin_user, get_current_user
import pandas as pd
import io

router = APIRouter()

@router.get("/", response_model=List[schemas.Book])
def get_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None
):
    query = db.query(models.Book)
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.author.ilike(f"%{search}%"),
                models.Book.isbn.ilike(f"%{search}%")
            )
        )
    if category:
        query = query.filter(models.Book.category == category)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Book)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    db_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for var, value in vars(book_update).items():
        if value is not None:
            setattr(db_book, var, value)
            
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}

@router.post("/bulk-upload")
def bulk_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")
    
    try:
        content = file.file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        books_added = 0
        for _, row in df.iterrows():
            # Check if ISBN already exists
            existing = db.query(models.Book).filter(models.Book.isbn == str(row['isbn'])).first()
            if not existing:
                db_book = models.Book(
                    isbn=str(row['isbn']),
                    title=row['title'],
                    author=row['author'],
                    publisher=row['publisher'],
                    category=row['category'],
                    edition=str(row['edition']),
                    year=int(row['year']),
                    total_copies=int(row['total_copies']),
                    available_copies=int(row['total_copies'])
                )
                db.add(db_book)
                books_added += 1
        
        db.commit()
        return {"message": f"Successfully added {books_added} books"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
