import os

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, RefreshToken, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST

app = Flask(__name__)
if os.environ.get('DATABASE_URL'):
    if os.environ.get('DATABASE_URL').startswith('postgres'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL').replace('postgres', 'postgresql')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.secret_key = 'tdd75'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_access_token(_identity):
    if _identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(_, payload):
    return payload["jti"] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return {
        'msg': 'The token has expired',
        'err': 'token_expired'
    }, 401


@jwt.invalid_token_loader
def invalid_token_callback():
    return {
        'msg': 'Signature verification failed.',
        'err': 'invalid_token'
    }, 401


@jwt.unauthorized_loader
def missing_token_callback():
    return {
        'msg': 'Request does not contain an access token.',
        'err': 'invalid_token'
    }, 401


@jwt.needs_fresh_token_loader
def not_fresh_token_callback():
    return {
        'msg': 'The token has not fresh',
        'err': 'fresh_token_required'
    }, 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return {
        'msg': 'The token has been revoked',
        'err': 'revoked_token'
    }, 401


api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(RefreshToken, '/refresh')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
