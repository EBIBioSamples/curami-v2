from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
import logging



from curami.web.forms import LoginForm
from curami.web import auth_service


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    form = LoginForm()

    if request.method == 'POST':
        if auth_service.authenticate_user(request.form['username'], request.form['password']):
            response = make_response(redirect(url_for('curation.get_curations', page=1, size=10)))
            response.set_cookie('username', request.form['username'])
            return response
            # return redirect(url_for('curation.get_curations', page=1, size=10))
        else:
            flash('Invalid username/password')
            return render_template('login.html', title='Sign In', form=form, error=error)
    else:
        return render_template('login.html', title='Sign In', form=form, error=error)


@auth.route('/logout', methods=['POST', 'GET'])
def logout(username):
    auth_service.logout(username)



