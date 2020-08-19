from flask import render_template, redirect, request, session, g, flash
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
import uuid
import requests

from app import app, db

from app.models.users import User

APP_ADDRESS = 'http://127.0.0.1:5000'

@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        g.token = None
    else:
        g.user = User.query.filter(User.id==user_id).first()
        g.token = get_token(g.user.username, g.user.password)

def authenticate(username, password):
    user = User.query.filter(User.username==username).first()
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.filter(User.id==user_id).first()

def create_user(username,password):
    return User(uuid.UUID,username,password)

def get_token(input_name, input_password):
    r = requests.post('{}/auth'.format(APP_ADDRESS),
                        json={
                            'username': input_name,
                            'password': input_password,
                        },
                        headers={'Content-type': 'application/json'}
                        )
    return r.json()["access_token"]

jwt = JWT(app, authenticate, identity)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

@app.route('/register', methods=['POST'])
def register():
    if request.form['username'] and request.form['password']:
        newUser = User(username=request.form['username'],
                       password=request.form['password'],
                       )
        db.session.add(newUser)
        db.session.commit()
        session['user_id'] = authenticate(input_name,input_password).id
        flash('Hello {}!'.format(requests.form['username']))
        return redirect('/')
 
    else:
        flash("error")
        return redirect('/signin')

@app.route('/login')
def login():
    return render_template('login.html',
                           title='Login Page',
                           app_address=APP_ADDRESS)
@app.route('/signup')
def signup():
    return render_template('signup.html',
                           title='Signup Page',
                           app_address=APP_ADDRESS)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('token', None)
    flash('Log out')
    return redirect('/')

@app.route('/authorize',methods=['POST'])
@jwt.auth_request_handler
def authorize():
    input_name = request.form['username']
    input_password = request.form['password']
    if authenticate(input_name,input_password):
        token = get_token(input_name, input_password)
        session['token'] = token
        session['user_id'] = authenticate(input_name,input_password).id
        flash('Login success!')
        return redirect('/')

    else:
        flash('Login failed')
        return redirect('/login')

@app.route('/user/<int:user_id>/edit')
def user_edit(user_id):
    return 'edit user ' + str(user_id)

