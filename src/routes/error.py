from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin

error = Blueprint("error", __name__)
cors = CORS(error, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@error.after_request 
@cross_origin(supports_credentials=True)
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Error handlers
@error.errorhandler(404)
@cross_origin(supports_credentials=True)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    print(message)
    response = jsonify(message)
    response.status_code = 404
    return response

@cross_origin(supports_credentials=True)
def data_not_match(error=None):
    message = {
        'message': 'Data do not match ' + request.url,
        'status': 404
    }
    print(message)
    response = jsonify(message)
    response.status_code = 404
    return response

@cross_origin(supports_credentials=True)
@error.errorhandler(500)
@cross_origin(supports_credentials=True)
def validation(status_error=500):
    message = {
        'message': 'The content does not correspond to the expected one. ' + request.url,
        'status': status_error
    }
    print(message)
    response = jsonify(message)
    response.status_code = status_error
    return response

@cross_origin(supports_credentials=True)
def already_exists():
    message = {
        'message': 'El usuario ya existe, por favor ingrese uno nuevo.',
        'status': 500
    }
    print(message)
    response = jsonify(message)
    response.status_code = 500
    return response

@cross_origin(supports_credentials=True)
def file_not_found():
    message = {
        'message' : 'No file selected for uploading ' + request.url,
        'status': 500
    }
    print(message)
    response = jsonify(message)
    response.status_code = 404
    return response

@cross_origin(supports_credentials=True)
def file_not_supported():
    message = {
        'message' : 'The only allowed audio type is .wav' + request.url,
        'status': 500
    }
    print(message)
    response = jsonify(message)
    response.status_code = 500
    return response

@cross_origin(supports_credentials=True)
def not_file():
    message = {
        'message' : 'No file part in the request' + request.url,
        'status': 500
    }
    print(message)
    response = jsonify(message)
    response.status_code = 500
    return response