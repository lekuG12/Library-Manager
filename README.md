# Library Manager

A Flask-based library management system for handling users, books, and transactions.

## Features

- User management (add, list, update, delete)
- Book management (add, list, update, delete, status)
- Borrow and return books
- Transaction tracking
- RESTful API endpoints
- Modular codebase using Flask Blueprints

## Project Structure

```
Library Manager/
├── app/
│   ├── APIs/           # API endpoints (users, books, transactions)
│   ├── Schema/         # SQLAlchemy models
│   ├── services/       # Business logic helpers (optional)
│   └── __init__.py     # App factory and blueprint registration
├── run.py              # Main entry point
├── requirements.txt    # Python dependencies
└── README.md
```

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. **Install PostgreSQL:**
   - Download and install PostgreSQL from [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
   - Create a database (e.g., `study_db`) and a user with the required credentials.
   - Update the connection string in `app/Schema/data.py` to match your PostgreSQL setup:
     ```python
     DB_URL = 'postgresql://username:password@localhost:5432/study_db'
     ```
   - Make sure PostgreSQL is running before starting your Flask app.
5. Run the application:
   ```
   python run.py
   ```

## API Usage

- Access endpoints via:
  - `/users` for user operations
  - `/books` for book operations
  - `/borrow` and `/return` for transactions

Use Postman or any HTTP client to interact with the API.

## License

MIT
