import logging

from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from curami.web import neo4j_connector


def authenticate_user(username, password):
    user_node = neo4j_connector.get_user(username)
    authenticated = False
    if user_node is not None:
        authenticated = check_password_hash(user_node['password'], password)

    if authenticated:
        session[username] = username
        logging.info('New user logged in {}', username)
    else:
        logging.warning('Wrong username/password')

    return authenticated


def check_user_session(username):
    session_exists = False
    if username in session:
        session_exists = True
    else:
        logging.warning("Session does not exist for user {}", username)

    return session_exists


def logout(username):
    session.pop(username)


def create_user(username, password):
    password_hash = generate_password_hash(password)
    neo4j_connector.create_user(username, password_hash)


if __name__ == '__main__':
    create_user('isuru', 'isuru')
    # authenticate_user('isuru', 'isuru')
