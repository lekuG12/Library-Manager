from flask import Blueprint, request
from app.Schema.data import Users, session, Base, engine
from sqlalchemy import text

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['POST'])
def add_users():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    with session() as db:
        new_user = Users(name=name, email=email, phone=phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return 'User created', 200


@user_bp.route('/user', methods=['GET'])
def list_users():
    try:
        with session() as db:
            users = db.query(Users).all()

            if users:
                return {'users': [ {'id': u.user_id, 'name': u.name, 'email': u.email, 'phone': u.phone } for u in users ]}
                
            else:
                return 'No user found'

    except Exception as e:
        return 'Error: {}'.format(e)


@user_bp.route('/users/<int:id>', methods=['GET'])
def by_id(id):

    with session() as db:
        user = db.query(Users).filter(Users.user_id == id).first()
    
    if user:
        return {
            'id': user.user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone
        }
    else:
        return 'User not found'

@user_bp.route('/users/<int:id>', methods=['PUT'])
def update(id):
    pass

@user_bp.route('/users/<int:id>', methods=['GET'])
def delete_user(id):
    with session() as db:
        user = db.query(Users).filter(Users.user_id == id).first()\
        
        if user:
            db.delete(user)
            db.commit()
        else:
            return 'User not found'
    
    return 'User deleted'

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)