import logging

from flask import Flask
from flask_cors import CORS, cross_origin
from curami.web.auth_controller import auth as auth_blueprint
from curami.web.curation_controller import app as curation_blueprint


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '_sdf5#y2L"F4Q8znxec]/'

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(curation_blueprint)

    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app, resources=r'/api/*', headers='Content-Type')

    # logging configuration
    logging.basicConfig(level=logging.INFO)

    return app


if __name__ == '__main__':
    create_app()
