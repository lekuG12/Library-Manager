from flask import Blueprint, request
from app.Schema.data import Transaction, Books, session
from datetime import datetime, timedelta

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/borrow', methods=['POST'])
def borrow():
    data = request.get_json()

    user_id = data.get('user_id')
    book_id = data.get('book_id')

    with session() as db:
       book = db.query(Books).filter(Books.book_id == book_id, Books.status == 'available').first()

       if not book or book.status != 'available':
           return {'Error': 'Book not available'}, 400
       
       due_date = datetime.utcnow() + timedelta(days=15)
       transactions = Transaction(user_id=user_id, book_id=book_id, due_date=due_date, status='borrowed')
       book.status = 'borrowed'

       db.add(transactions)
       db.commit()
       db.refresh(transactions)

    return {'message': 'Book borrowed', 'transaction_id': transactions.transaction_id}


@transaction_bp.route('/return', methods=['POST'])
def return_book():
    data = request.get_json()

    user_id = data.get('user_id')
    book_id = data.get('book_id')

    with session() as db:
        transaction = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.book_id == book_id, Transaction.status == 'borrowed').first()
        if not transaction:
            return {'error': 'Active transaction not found'}, 404
        transaction.return_date = datetime.utcnow()
        transaction.status = 'returned'
        # Update book status
        book = db.query(Books).filter(Books.book_id == book_id).first()
        book.status = 'available'
        db.commit()
        db.refresh(transaction)

    return {'message': 'Book returned', 'transaction_id': transaction.transaction_id}


@transaction_bp.route('/transaction', methods=['GET'])
def transact():
    with session() as db:
       transactions = db.query(Transaction).all()

       if not transactions:
              return {'message': 'No transactions found'}, 404
       return {
           'transactions': [
               {
                   'id': t.transaction_id,
                   'user_id': t.user_id,
                   'book_id': t.book_id,
                   'borrwed_date': t.borrow_date,
                   'due_date': t.due_date,
               }
           ] for t in transactions
       }
