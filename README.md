# Enterprise Library Management System (ELMS)

A production-ready, enterprise-grade digital platform for institutional library operations. Built with a focus on scalability, security, and a premium user experience.

##  Key Features

### 1. Authentication & Security
- **JWT-Based Auth:** Secure session management using JSON Web Tokens.
- **Role-Based Access Control (RBAC):** Distinct workflows for **Librarians (Admin)** and **Members (Students/Employees)**.
- **Secure Password Hashing:** Powered by BCrypt.

### 2. Catalog & Inventory
- **Full CRUD Support:** Add, update, and manage the book inventory with ease.
- **Bulk Upload:** Fast-track inventory setup with CSV support.
- **Global Search:** Instant filtering by ISBN, Title, Author, or Category.

### 3. Borrowing & Logistics
- **Smart Due Dates:** Automated calculation based on institutional policy (14-day default).
- **Availability Tracking:** Real-time updates on book stock levels.
- **Fine Management:** Automated calculation of overdue penalties ($10/day).
- **Reservations:** Automated queue system when books are unavailable.

### 4. Insights & Auditing
- **Administrative Dashboard:** Real-time metrics on issued books, overdue items, and active members.
- **Audit Trails:** Centralized logs for library activities.

##  Technology Stack

- **Backend:** FastAPI (Python 3.9+)
- **Database:** SQLite (SQLAlchemy ORM) - Ready for PostgreSQL migration.
- **Frontend:** Vanilla JavaScript (ES6+), Modern CSS (Custom Design System).
- **API Docs:** Interactive Swagger UI (OpenAPI).

## 📂 Project Structure

```text
lib-management/
├── backend/
│   ├── app/
│   │   ├── routes/      # API Controllers
│   │   ├── models.py    # Database Schema
│   │   ├── schemas.py   # Pydantic Validation
│   │   ├── auth.py     # JWT & Security
│   │   └── main.py     # Entry Point
│   ├── seed.py         # Sample Data Generator
│   └── requirements.txt
└── frontend/
    ├── index.html      # Auth Entry
    ├── dashboard.html  # Main Application
    ├── css/            # Premium Styles
    └── js/             # API & App Logic
```

##  Setup Instructions

### 1. Backend Setup
1. Navigate to the `backend` folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Seed the database with sample data:
   ```bash
   python seed.py
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### 2. Frontend Setup
- Simply open `frontend/index.html` in your browser.
- **Default Credentials:**
  - **Admin:** `admin@library.com` / `admin123`
  - **Member:** `student@university.edu` / `student123`

##  Future Roadmap
- [ ] Integration with Email/SMS for due date alerts.
- [ ] Barcode/QR Code scanning for quick book returns.
- [ ] Integrated Payment Gateway for fine payments.
- [ ] Advanced PDF/Excel report exporting.

---
*Designed with ❤️ for institutional excellence.*
