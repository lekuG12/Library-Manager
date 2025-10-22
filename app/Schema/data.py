from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, DATE
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

Base = declarative_base()

# Use an in-memory SQLite engine when running tests to avoid external DB dependency
if os.environ.get('TESTING', '').lower() in ('1', 'true', 'yes'):
    DB_URL = 'sqlite:///:memory:'
else:
    DB_URL = 'postgresql://username:password@localhost:5432/study_db'
engine = create_engine(DB_URL)

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), unique=True, nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    phone = Column(String(80), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow())

    transaction = relationship('Transaction', back_populates='user')

class Books(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False, unique=True)
    isbn = Column(String(250), unique=True)
    author = Column(String(250))
    category = Column(String(250))
    status = Column(String(50), default='available')
    created_at = Column(DateTime, default=datetime.utcnow())

    transaction = relationship('Transaction', back_populates='book')

class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    book_id = Column(Integer, ForeignKey('books.book_id'))
    borrow_date = Column(DateTime, nullable=False, default=datetime.utcnow())
    due_date = Column(DateTime, nullable=False)
    return_date = (DateTime)
    status = Column(String(50))

    book = relationship('Books', back_populates='transaction')
    user = relationship('Users', back_populates='transaction')


session = sessionmaker(bind=engine)
# Only attempt to create tables when not using ephemeral in-memory DB in import time
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # In tests, table creation can be skipped; routes patch session() anyway
    pass