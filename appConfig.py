# IMPORTS - START
import flask
import os
import re
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import pandas as pd
from datetime import datetime, date
from dateutil import relativedelta
import shutil
import csv
import matplotlib.pyplot as plt
# IMPORTS - END

# GLOBAL VARIABLES - START
app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
login_manager.init_app(app)
db = SQLAlchemy(app)

raceEthDict = {
    'A': 'Asian',
    'B': 'Black',
    'H': 'Hispanic',
    'I': 'TBD - I',
    'P': 'TBD - P',
    'S': 'TBD - S',
    'U': 'TBD - U',
    'W': 'White'
}

genderDict = {
    'F': 'Female',
    'M': 'Male',
    'Non Binary': 1,
    'Not Declared': 1
}

employeeDict = {
    'Professional': 1,
    'Academic': 1,
    'State Classified': 1
}
# GLOBAL VARIABLES - END
