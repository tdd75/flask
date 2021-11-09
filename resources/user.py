import sqlite3
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from flask_jwt_extended.utils import get_jwt, get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource, reqparse
from blacklist import BLACKLIST
from models.user import UserModel
from werkzeug.security import safe_str_cmp


_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username', type=str, required=True,
                          help='This field cannot be blank.')
_user_parser.add_argument('password', type=str, required=True,
                          help='This field cannot be blank.')


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': 'User created successfully'}, 201


class User(Resource):
    @classmethod
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404

    @classmethod
    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {'messgae': 'User deleted'}, 200
        return {'message': 'User not found'}, 404


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        return {'message': 'Invalid credentials'}, 401

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=True)
        return {'access_token': new_token}, 200

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'}, 200