from flask import Flask, request
from app.Schema.data import Transaction, Books, Users, session
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/borrow', methods=['POST'])
def borrow():
    data = request.get_json()

    user_id = data.get('user_id')
    book_id = data.get('book_id')

    with session() as db:
        book = db.query(Books).filter(Books.book_id == book_id).first()
        if not book or book.status != 'available':
            return {'error': 'Book not available'}, 400
        # Create transaction
        due_date = datetime.utcnow() + timedelta(days=14)
        transaction = Transaction(user_id=user_id, book_id=book_id, borrow_date=datetime.utcnow(), due_date=due_date, status='borrowed')
        db.add(transaction)
        # Update book status
        book.status = 'borrowed'
        db.commit()
        db.refresh(transaction)

    return {'message': 'Book borrowed', 'transaction_id': transaction.transaction_id}


@app.route('/return', methods=['POST'])
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


@app.route('/transaction', methods=['GET'])
def transact():
    with session() as db:
        transactions = db.query(Transaction).all()
        return {'transactions': [
            {
                'id': t.transaction_id,
                'user_id': t.user_id,
                'book_id': t.book_id,
                'borrow_date': t.borrow_date,
                'due_date': t.due_date,
                'return_date': t.return_date,
                'status': t.status
            } for t in transactions
        ]}


if __name__ == '__main__':
    app.run(debug=True)