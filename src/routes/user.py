from flask import Blueprint, current_app, request, jsonify, Response, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from src.database.connection import db
import src.database.schemas as schemas
import src.routes.error as error
from flask_cors import CORS, cross_origin


user = Blueprint("user", __name__)
cors = CORS(user, resources={r"/*": {"origins": "*"}}, support_credentials=True)


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@user.after_request 
@cross_origin(supports_credentials=True)
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@user.route('/', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def create_user():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    # Receiving data
    data = request.form.to_dict()
    current_app.logger.info(data)
    
    if data['password'] == data['confirm_password']:
        # Encrypting password.
        data['password'] = generate_password_hash(data['password'])
        data['age'] = int(data['age'])
        del data['confirm_password']
        # Validate User Schema
        try:
            # Validating mongodb schema.
            user_schema = schemas.get_user_schema()
            validate(instance=data, schema=user_schema)
            # Removing white spaces from string fields.
            for field in ['name', 'email', 'username', 'password']:
                data[field] = data[field].strip()
            # Prev user exists validation.
            prev_usr = db.users.find_one({
                '$or': [
                        {'username': data['username']}, 
                        {'email': data['email']}
                    ]
                })
            if not prev_usr:
                result = db.users.insert_one(data)
            else: 
                return error.already_exists()
        except ValidationError as e:
            current_app.logger.error(str(e))
            return error.validation()
        # Giving a response to the server.
        response = jsonify({'login': True, 'user_id': str(result.inserted_id)})
        response.status_code = 200
        return response

    return error.data_not_match()


@user.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_users():
    # Retrieving data
    users = db.users.find({})
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")


@user.route('/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user(id):
    # Retrieving user data by id.
    user = db.users.find_one({ '_id': ObjectId(id) })
    response = json_util.dumps(user)
    res = Response(response, mimetype="application/json")
    return res

@user.route('/username/<id>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_username(id):
    # Retrieving user data by id.
    user = db.users.find_one({ '_id': ObjectId(id) })
    response = json_util.dumps({'username': user['username']})
    res = Response(response, mimetype="application/json")
    return res


@user.route('/<id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_user(id):
    # Deleting user data.
    db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': f'User {id} deleted successfully.'})
    response.status_code = 200
    return response


@user.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def validate_login():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    # Receiving data
    data = request.form.to_dict()
    current_app.logger.info(data)
    usr = db.users.find_one({'username': data['username']})
    response = jsonify({'login': False})
    if usr:        
        if check_password_hash(usr['password'], data['password']):
            response = jsonify({'login': True, 'user_id': str(usr['_id'])}) 
    response.status_code = 200
    return response