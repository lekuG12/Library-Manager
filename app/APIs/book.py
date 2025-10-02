from flask import Flask, request
from app.Schema.data import Books, session, Base, engine

app = Flask(__name__)

@app.route('/books', methods=['POST'])
def add_users():
    data = request.get_json()
    title = data.get('title')
    isbn = data.get('isbn')
    author = data.get('author')
    category = data.get('category')

    with session() as db:
        new_book = Books(title=title, isbn=isbn, author=author, category=category)
        db.add(new_book)
        db.commit()
        db.refresh(new_book)

    return 'Book created', 200


@app.route('/book', methods=['GET'])
def list_books():
    try:
        with session() as db:
            results = db.query(Books).all()
            if results:
                return {'books': [ {'id': b.book_id, 'title': b.title, 'isbn': b.isbn, 'author': b.author, 'status': b.status } for b in results ]}    
            else:
                return 'No books found'
    except Exception as e:
        return 'Error: {}'.format(e)


@app.route('/books/<int:id>', methods=['GET'])
def by_id(id):

    with session() as db:
        book = db.query(Books).filter(Books.book_id == id).first()
    
    if book:
        return {
            'id': book.book_id,
            'title': book.title,
            'isbn': book.isbn,
            'author': book.author,
            'category': book.category,
            'status': book.status
        }

@app.route('/books/<int:id>', methods=['PUT'])
def update(id):
    pass

@app.route('/books/<int:id>', methods=['GET'])
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