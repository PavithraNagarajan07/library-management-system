from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .database import Base
import datetime
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class BorrowStatus(str, enum.Enum):
    REQUESTED = "requested"
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"

class FineStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    WAIVED = "waived"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    borrows = relationship("Borrow", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    publisher = Column(String)
    category = Column(String, index=True)
    edition = Column(String)
    year = Column(Integer)
    total_copies = Column(Integer)
    available_copies = Column(Integer)
    
    borrows = relationship("Borrow", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")

class Borrow(Base):
    __tablename__ = "borrows"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(DateTime, default=datetime.datetime.utcnow)
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(BorrowStatus), default=BorrowStatus.BORROWED)
    fine_amount = Column(Float, default=0.0)

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")
    fine_records = relationship("Fine", back_populates="borrow")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    reservation_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="pending") # pending, fulfilled, cancelled

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

class Fine(Base):
    __tablename__ = "fines"
    id = Column(Integer, primary_key=True, index=True)
    borrow_id = Column(Integer, ForeignKey("borrows.id"))
    amount = Column(Float)
    status = Column(SQLEnum(FineStatus), default=FineStatus.UNPAID)
    payment_date = Column(DateTime, nullable=True)

    borrow = relationship("Borrow", back_populates="fine_records")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    target_type = Column(String)
    target_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
