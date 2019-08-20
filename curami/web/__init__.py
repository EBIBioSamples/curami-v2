from flask import Flask
from curami.web.auth_controller import auth as auth_blueprint
from curami.web.curation_controller import app as curation_blueprint


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '_sdf5#y2L"F4Q8znxec]/'

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(curation_blueprint)

    return app


if __name__ == '__main__':
    create_app()
