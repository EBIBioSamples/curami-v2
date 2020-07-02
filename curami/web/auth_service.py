import logging
import random

from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from curami.commons import neo4j_connector


def authenticate_user(username, password):
    user_node = neo4j_connector.get_user(username)
    authenticated = False
    token = None
    if user_node is not None:
        authenticated = check_password_hash(user_node['password'], password)

    if authenticated:
        token = random.getrandbits(128)
        session[username] = token
        logging.info('New user logged in %s', username)
    else:
        logging.warning('Invalid username/password %s', username)

    return token


def check_user_session(username):
    session_exists = False
    if username in session:
        session_exists = True
    else:
        logging.warning("Session does not exist for user %s", username)

    return session_exists


def logout(username):
    session.pop(username)


def create_user(username, password):
    password_hash = generate_password_hash(password)
    neo4j_connector.create_user(username, password_hash)


if __name__ == '__main__':
    create_user('isuru', 'isuru')
