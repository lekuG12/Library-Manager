from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DATE
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DB_URL = 'postgresql://postgres:Sensei_237@127.0.0.1:5432/study_db'
engine = create_engine(DB_URL)

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), unique=True, nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    phone = Column(String(80), unique=True)
    created_at = Column(DATE)

    transaction = relationship('Transaction', back_populates='users')

class Books(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False, unique=True)
    isbn = Column(String(250), unique=True)
    author = Column(String(250))
    category = Column(String(250))
    status = Column(String(50))
    created_at = Column(DATE)

    transaction = relationship('Transaction', back_populates='books')

class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    book_id = Column(Integer, ForeignKey('books.book_id'))
    borrow_date = Column(DATE, nullable=False)
    due_date = Column(DATE, nullable=False)
    return_date = (DATE)
    status = Column(String(50))

    book = relationship('Books', back_populates='transaction')
    user = relationship('Users', back_populates='transaction')


session = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)