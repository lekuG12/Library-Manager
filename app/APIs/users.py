from flask import Flask, request
from app.Schema.data import Users, session, Base, engine
from sqlalchemy import text

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def add_users():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    created_at = request.form.get('datetime')

    with session as db:
        new_user = Users(name=name, email=email, phone=phone, created_at=created_at)
        db.add(new_user)
        db.commit()
        db.refresh()

    return 'User created', 200


@app.route('/user', methods=['GET'])
def list_users():
    try:
        with engine.connect() as connection:
            results = connection.execute(text('SELECT name FROM users'))

            users = results.fetchall()

            if users:
                for user in users:
                    return f'- {user[0]}'
                
            else:
                return 'No user found'

    except Exception as e:
        return 'Error: {}'.format(e)


@app.route('/users/<int:id>', methods=['GET'])
def by_id(id):

    with session as db:
        user = db.query(Users).filter(Users.user_id == id).first()
    
    return user

@app.route('/users/<int:id>', methods=['PUT'])
def update(id):
    pass

@app.route('/users/<int:id>', methods=['GET'])
def delete_user(id):
    with session as db:
        user = db.query(Users).filter(Users.user_id == id).first()\
        
        if user:
            db.delete(user)
            db.commit()
        else:
            return 'User not found'
    
    return 'User deleted'

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)