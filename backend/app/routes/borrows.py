from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from .. import models, schemas, database
from ..database import get_db
from .users import get_current_user, get_admin_user

router = APIRouter()

FINE_RATE_PER_DAY = 10.0 # Configurable fine rate

@router.post("/request", response_model=schemas.Borrow)
def request_book(
    request: schemas.BorrowBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if book exists and is available
    book = db.query(models.Book).filter(models.Book.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.available_copies <= 0:
        # Create reservation if not available
        reservation = models.Reservation(user_id=current_user.id, book_id=book.id)
        db.add(reservation)
        db.commit()
        raise HTTPException(status_code=400, detail="Book is currently unavailable. A reservation has been placed.")

    # Check if user already has this book borrowed
    existing = db.query(models.Borrow).filter(
        models.Borrow.user_id == current_user.id,
        models.Borrow.book_id == book.id,
        models.Borrow.status.in_([models.BorrowStatus.BORROWED, models.BorrowStatus.OVERDUE])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already have this book")

    # Borrow duration (e.g., 14 days)
    due_date = datetime.utcnow() + timedelta(days=14)
    
    borrow = models.Borrow(
        user_id=current_user.id,
        book_id=book.id,
        due_date=due_date,
        status=models.BorrowStatus.BORROWED
    )
    
    book.available_copies -= 1
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

@router.post("/{borrow_id}/return", response_model=schemas.Borrow)
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id).first()
    if not borrow or borrow.status == models.BorrowStatus.RETURNED:
        raise HTTPException(status_code=404, detail="Active borrow record not found")

    borrow.return_date = datetime.utcnow()
    borrow.status = models.BorrowStatus.RETURNED
    
    # Calculate fine if overdue
    if borrow.return_date > borrow.due_date:
        overdue_days = (borrow.return_date - borrow.due_date).days
        if overdue_days > 0:
            fine_amount = overdue_days * FINE_RATE_PER_DAY
            borrow.fine_amount = fine_amount
            fine = models.Fine(borrow_id=borrow.id, amount=fine_amount)
            db.add(fine)

    # Update book availability
    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    book.available_copies += 1
    
    # Check for reservations
    reservation = db.query(models.Reservation).filter(
        models.Reservation.book_id == book.id,
        models.Reservation.status == "pending"
    ).order_by(models.Reservation.reservation_date).first()
    
    if reservation:
        # In a real system, you'd notify the user. 
        # Here we just mark it as potentially fulfilled
        pass

    db.commit()
    db.refresh(borrow)
    return borrow

@router.get("/my-history", response_model=List[schemas.Borrow])
def get_my_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Borrow).filter(models.Borrow.user_id == current_user.id).all()

@router.get("/all", response_model=List[schemas.Borrow])
def get_all_borrows(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    return db.query(models.Borrow).all()

@router.post("/fine/{fine_id}/pay")
def pay_fine(
    fine_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    fine = db.query(models.Fine).filter(models.Fine.id == fine_id).first()
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    fine.status = models.FineStatus.PAID
    fine.payment_date = datetime.utcnow()
    db.commit()
    return {"message": "Fine paid successfully"}
