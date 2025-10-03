from flask import Flask
from app.APIs.users import user_bp
from app.APIs.book import book_bp
from app.APIs.transaction import transaction_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(transaction_bp)
    return app

app = create_app()