import flask
import os
import re
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import pandas as pd
from datetime import datetime


#df = pd.read_csv('tempFileName.csv')
def hireDateConversion():
    df['Hire Date'] = pd.to_datetime(df['Hire Date'])
    current_date = datetime.now()
    df['Years Since Hire'] = (current_date - df['Hire Date']).dt.days / 365.25
    print(df)



app = Flask(__name__, static_url_path='/static')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    return render_template('createGraph.html')

if __name__ == "__main__":
    app.run(debug=True)