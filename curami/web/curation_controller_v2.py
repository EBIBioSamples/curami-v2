from flask import render_template, request, abort, Blueprint, jsonify, make_response, redirect, url_for
from curami.web import curation_service_v2 as curation_service, helper_service, auth_service_v2 as auth_service

app = Blueprint('curation_v2', __name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user')
def user_summary():
    username = request.cookies.get('username')
    if username is None:
        username = 'guest'
    return render_template('profile.html', username=username)


@app.route('/curations', methods=['GET'])
def get_curations():
    page = int(request.args.get('page', default=1))
    size = int(request.args.get('size', default=10))

    token = request.headers.get('token')
    user = request.headers.get('user')
    authenticated = auth_service.check_user_session(user, token)
    print("auth status: " + str(authenticated) + " : " + str(token))

    if not authenticated:
        abort(403, description='Not authenticated')

    curations = curation_service.get_curations(page, size, user)
    return jsonify(curations)


@app.route('/curations', methods=['POST'])
def apply_curation():
    token = request.headers.get('token')
    user = request.headers.get('user')
    authenticated = auth_service.check_user_session(user, token)
    print("auth status: " + str(authenticated) + " : " + str(token))

    if not authenticated:
        abort(403, description='Not authenticated')

    curation = curation_service.save_curation(request.get_json(), user)
    return jsonify(curation)


@app.route('/summary')
def show_summary():
    username = request.cookies.get('username')
    if username is None:
        username = 'guest'
    return render_template('summary.html', name=username)


@app.route('/test/')
@app.route('/test/<name>')
def test(name):
    return render_template('summary.html', name=name)


@app.route('/error')
def error_page():
    abort(401)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.errorhandler(helper_service.InvalidMessage)
def handle_invalid_messages(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

