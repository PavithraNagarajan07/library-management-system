from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, database
from ..database import get_db
from .users import get_admin_user

router = APIRouter()

@router.get("/admin", response_model=schemas.DashboardStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    total_books = db.query(models.Book).count()
    active_members = db.query(models.User).filter(models.User.role == models.UserRole.MEMBER, models.User.is_active == True).count()
    books_issued = db.query(models.Borrow).filter(models.Borrow.status == models.BorrowStatus.BORROWED).count()
    overdue_books = db.query(models.Borrow).filter(models.Borrow.status == models.BorrowStatus.OVERDUE).count()
    
    fine_collection = db.query(func.sum(models.Fine.amount)).filter(models.Fine.status == models.FineStatus.PAID).scalar() or 0.0
    
    return {
        "total_books": total_books,
        "active_members": active_members,
        "books_issued": books_issued,
        "overdue_books": overdue_books,
        "fine_collection": fine_collection
    }

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_admin_user)
):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(100).all()

@router.get("/member")
def get_member_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user) # Using get_admin_user for simplicity or define get_current_user
):
    # This will be handled on the frontend by calling personal history and filters
    pass
