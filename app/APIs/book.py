from flask import Flask, request
from app.Schema.data import Books, session, Base, engine
from services.main import status

app = Flask(__name__)

@app.route('/books', methods=['POST'])
def add_users():
    title = request.form.get('title')
    isbn = request.form.get('isbn')
    author = request.form.get('author')
    stat = status()
    created_at = request.form.get('datetime')

    with session as db:
        new_book = Books(title=title, isbn=isbn, author=author, status=stat, created_at=created_at)
        db.add(new_book)
        db.commit()
        db.refresh()

    return 'Book created', 200


@app.route('/book', methods=['GET'])
def list_users():
    pass


@app.route('/books/<int:id>', methods=['GET'])
def by_id(id):

    with session as db:
        user = db.query(Books).filter(Books.book_id == id).first()
    
    return user

@app.route('books/<int:id>', methods=['PUT'])
def update(id):
    pass

@app.route('books/<int:id>', methods=['GET'])
def delete_user(id):
    with session as db:
        user = db.query(Books).filter(Books.book_id == id).first()\
        
        if user:
            db.delete(user)
            db.commit()
        else:
            return 'User not found'
    
    return 'Book deleted'

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)