from flask import Blueprint, request, jsonify

from curami.web import auth_service_v2 as auth_service

auth = Blueprint('auth_v2', __name__)


@auth.route('/login', methods=['POST'])
def login():
    response = dict()
    request_json = request.get_json()
    token = auth_service.authenticate_user(request_json["username"], request_json["password"])
    if token:
        response["status"] = True
        response["token"] = token
    else:
        response["status"] = False
    return jsonify(response)


@auth.route('/logout', methods=['POST'])
def logout():
    request_json = request.get_json()
    logged_out = auth_service.logout(request_json["username"])
    return jsonify(logged_out)
