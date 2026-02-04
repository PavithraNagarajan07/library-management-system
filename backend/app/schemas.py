from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .models import UserRole, BorrowStatus, FineStatus

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MEMBER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    category: str
    edition: str
    year: int
    total_copies: int
    available_copies: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    category: Optional[str] = None
    edition: Optional[str] = None
    year: Optional[int] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None

class Book(BookBase):
    id: int

    class Config:
        orm_mode = True

class BorrowBase(BaseModel):
    book_id: int

class BorrowCreate(BorrowBase):
    user_id: int
    due_date: datetime

class Borrow(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatus
    fine_amount: float
    book: Book

    class Config:
        orm_mode = True

class FineBase(BaseModel):
    borrow_id: int
    amount: float

class Fine(FineBase):
    id: int
    status: FineStatus
    payment_date: Optional[datetime] = None

    class Config:
        orm_mode = True

class ReservationBase(BaseModel):
    book_id: int

class Reservation(ReservationBase):
    id: int
    user_id: int
    reservation_date: datetime
    status: str

    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    total_books: int
    active_members: int
    books_issued: int
    overdue_books: int
    fine_collection: float
