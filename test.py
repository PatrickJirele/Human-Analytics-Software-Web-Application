import flask
import os
import re
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import pandas as pd
from datetime import datetime, date
import shutil

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
login_manager.init_app(app)
db = SQLAlchemy(app)


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        print("Valid")
        return True
    else:
        print("Invalid")
        return False



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if check(email) == True:
            user = User.query.filter_by(email=email).first()
            if user != None:
                if request.form['pWord'] != user.password:
                    return render_template('login.html')
                else:
                    login_user(user)
                    return flask.redirect('/')
            return render_template('login.html')
        else:
            return render_template('/')
    return render_template('login.html')

@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect('/')

@app.route('/updatePassword', methods = ['GET', 'POST'])
@login_required
def updatePass():
    if request.method == 'POST':
        oldPassword = request.form['oldP']
        if current_user.password != oldPassword:
            return render_template('updatePassword.html')
        updatedUser = User.query.filter_by(id=current_user.id).first()
        updatedUser.password = request.form['newP']
        db.session.commit()
        return flask.redirect('/')
    return render_template('updatePassword.html')

@login_required
@app.route('/createAdmin', methods = ['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pWord']
        if check(email) == False:
            return render_template('createAdmin.html'), 'Invalid Email Address'
        temp = User(email = email, password = password)
        user = User.query.filter_by(email=request.form['email']).first()
        if user != None:
            return render_template('createAdmin.html'), 'user already exists'
        else:
            db.session.add(temp)
            db.session.commit()
            user = User.query.filter_by(email=request.form['email']).first()
            login_user(user)
            return flask.redirect('/')
    return render_template('createAdmin.html')

@login_required
@app.route('/uploadDataset', methods = ['GET', 'POST'])
def uploadDataset():
    """
    get file name, then save the file
    set the destination folder
    check if file for the same date exists, if it does remove it(could be edited later)
    rename the file, then save it to datasets folder
    delete the file from project directory
    """
    if request.method == 'POST':
        file = request.files['file']
        file.save(file.filename)
        destination = './static/datasets'
        newFileName = str(date.today())+'.xlsx'
        if os.path.isfile(newFileName):
            os.remove(newFileName)
        os.rename(file.filename, newFileName)
        shutil.copy2(newFileName, destination)
        os.remove(newFileName)


    return render_template('uploadDataset.html')

@login_required
@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    return render_template('createGraph.html')

if __name__ == "__main__":
    app.run(debug=True)