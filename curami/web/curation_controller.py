from flask import render_template, request, abort, Blueprint, jsonify, make_response, redirect, url_for
from curami.web import curation_service, helper_service, auth_service

app = Blueprint('curation', __name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user')
def user_summary():
    username = request.cookies.get('username')
    if username is None:
        username = 'guest'
    return render_template('profile.html', username=username)


@app.route('/curations', methods=['GET', 'POST'])
def get_curations():
    username = request.cookies.get('username')
    # if username is None:
    #     username = 'guest'

    if username is None and not auth_service.check_user_session(username):
        response = make_response(redirect(url_for('auth.login')))
        return response

    if request.method == 'GET':
        page = int(request.args.get('page', default=1))
        size = int(request.args.get('size', default=10))

        if page < 1:
            page = 1

        curations = curation_service.get_curations(page, size, username)
        return render_template('curate.html', curations=curations, page=page, size=size)
    elif request.method == 'POST':
        curation_service.save_curation(request.get_json(), username)
        return jsonify(request.get_json())


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

#
# with app.test_request_context():
#     print(url_for('login'))
#     print(url_for('static', filename='styles.css'))
