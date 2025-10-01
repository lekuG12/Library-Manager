from flask import Flask

app = Flask(__name__)

@app.route('/borrow', methods=['POST'])
def borrow():
    pass

@app.route('/return', methods=['POST'])
def return_book():
    pass

@app.route('/transaction', methods=['GET'])
def transact():
    pass


if __name__ == '__main__':
    app.run(debug=True)