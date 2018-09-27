import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
     create_refresh_token, 
     jwt_refresh_token_required,
     get_jwt_identity,
     jwt_required, 
     get_raw_jwt)
from werkzeug.security import safe_str_cmp
from models.user import UserModel
from blacklist import BLACKLIST

def parse_data():
    parser = reqparse.RequestParser()
    parser.add_argument('username', 
        type=str, 
        required=True, 
        help="This field cannot be left blank")
    parser.add_argument('password', 
        type=str, 
        required=True, 
        help="This field cannot be left blank")
    return parser.parse_args()

class UserRegister(Resource):
    def post(self):
        req_data = parse_data()
        if UserModel.find_by_username(req_data['username']):
            return {"message": "User '{}' already exist.".format(req_data['username'])}, 400

        user = UserModel(**req_data)
        user.save()

        return {"message": "User '{}' created successfully.".format(req_data['username'])}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.json()

    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        req_data = parse_data()
        user = UserModel.find_by_username(req_data['username'])

        # Note: This is similar to what the authenticate() function used to do.
        if user and safe_str_cmp(user.password, req_data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        
        return {'message': 'Invalid credentials'}, 401

class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # jti is "JWT ID", a unique identifier for a jwt
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'}, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {'access_token': new_token}, 200