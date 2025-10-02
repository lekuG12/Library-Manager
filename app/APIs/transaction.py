from flask import Flask, request
from app.Schema.data import Transaction, session, Base, engine

app = Flask(__name__)

@app.route('/borrow', methods=['POST'])
def borrow():
    data = request.get_json()
    

@app.route('/return', methods=['POST'])
def return_book():
    pass

@app.route('/transaction', methods=['GET'])
def transact():
    pass


if __name__ == '__main__':
    app.run(debug=True)