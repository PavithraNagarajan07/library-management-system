from app.database import SessionLocal, engine
from app import models, auth
from datetime import datetime, timedelta

def seed():
    db = SessionLocal()
    models.Base.metadata.create_all(bind=engine)

    # Create Admin
    admin = db.query(models.User).filter(models.User.email == "admin@library.com").first()
    if not admin:
        admin = models.User(
            email="admin@library.com",
            full_name="System Librarian",
            hashed_password=auth.get_password_hash("admin123"),
            role=models.UserRole.ADMIN
        )
        db.add(admin)

    # Create Member
    member = db.query(models.User).filter(models.User.email == "student@university.edu").first()
    if not member:
        member = models.User(
            email="student@university.edu",
            full_name="John Doe",
            hashed_password=auth.get_password_hash("student123"),
            role=models.UserRole.MEMBER
        )
        db.add(member)

    # Add Books
    books_data = [
        {
            "isbn": "978-0132350884",
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "category": "Computer Science",
            "edition": "1st",
            "year": 2008,
            "total_copies": 5,
            "available_copies": 5
        },
        {
            "isbn": "978-0201633610",
            "title": "Design Patterns",
            "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
            "publisher": "Addison-Wesley",
            "category": "Software Engineering",
            "edition": "1st",
            "year": 1994,
            "total_copies": 3,
            "available_copies": 3
        },
        {
            "isbn": "978-0596007126",
            "title": "Head First Design Patterns",
            "author": "Eric Freeman, Bert Bates, Kathy Sierra, Elisabeth Robson",
            "publisher": "O'Reilly Media",
            "category": "Programming",
            "edition": "1st",
            "year": 2004,
            "total_copies": 4,
            "available_copies": 4
        }
    ]

    for b in books_data:
        existing = db.query(models.Book).filter(models.Book.isbn == b["isbn"]).first()
        if not existing:
            book = models.Book(**b)
            db.add(book)

    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed()
