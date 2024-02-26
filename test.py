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

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
login_manager.init_app(app)
db = SQLAlchemy(app)

#Validates if entered email is in correct format
def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        print("Valid")
        return True
    else:
        print("Invalid")
        return False


# TO DO:
# Combine Race & Ethnicity

# originalFileName = 'data.csv'
# destinationFileName = 'preprocessed.csv'
maxNumberOfMissingCells = 2

# UNABBREVIATION DICTIONARIES
# Note: If a key:value pair has a value of 1, the key will be used as the unabbreviation.

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

# PRECONDITION: Any dataframe is provided that may or may not contain a "Name" column.
# POSTCONDITION: The dataframe is returned without a "Name" column.
def dropNameColumn(df):
    try:
        df = df.drop('Name', axis=1)
    except:
        print('Column "Name" does not exist.')
    return df

# PRECONDITION: A dataframe is provided containing both a "Race" and "Ethnicity" column.
# POSTCONDITION: The dataframe is returned with neither of the above columns, and instead it contains a "Race/Ethnicity" column that displays the previous information
#                of their respective columns. The ethnicity value take priority.
def combineRaceAndEthnicity(df):
    return df


# PRECONDITION: A dataframe is provided containing a column named "Years At Western" with values formated at "%m/%d/%Y"
# POSTCONDITION: The dataframe is returned with every value in the "Years At Western" column reformatted as the number of years since the current date, rounded down.
def reformatYearsColumn(df):
    columnName = 'Years At Western'
    for i in range(len(df)):
        value = df.loc[i, columnName]
        try:
            date = datetime.strptime(value, "%m/%d/%Y")
            rd = relativedelta.relativedelta(datetime.now(), date)
            df.loc[i,columnName] = rd.years
        except Exception as e:
            print(e)
            df.loc[i,columnName] = ''
    return df

# PRECONDITION: A dataframe is provided with the columns "Race/Ethnicity", "Gender", and "Employee Type".
# POSTCONDITION: The dataframe is returned with all info unabreviated and invalid values removed. Entire rows with multiple invalid values are potentially removed
#                depending on maxNumberOfMissingCells value.
def formatData(df):
    for columnName, values in [('Race/Ethnicity', raceEthDict), ('Gender',genderDict), ('Employee Type', employeeDict)]:
        formatDataPerColumn(df, columnName, values)
    df.dropna(thresh=maxNumberOfMissingCells, inplace = True);
    df.replace('', 'NaN', inplace = True)
    return df

# PRECONDITION: A dataframe is provided with a column with the same name as the value columnName. A valid dictionary related to the columnName is also provided.
# POSTCONDITION: Each value in the provided column is matched against the dictionary. If the value is valid, the value is replaced with its unabreviated form.
#                If the value is invalid, it is removed.
def formatDataPerColumn(df, columnName, values):
    for i in range(len(df)):
        value = df.loc[i, columnName]
        if (value not in values):
            df.loc[i,columnName] = ''
        else:
            if (values[value] != 1):
                df.loc[i, columnName] = values[value]
    return df




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
    if request.method == 'POST':
        #Get the excel file from website upload
        file = request.files['file']
        file.save(file.filename)
        destination = './static/datasets'
        newFileName = str(date.today())+'.csv'
        if os.path.isfile(newFileName):
            os.remove(newFileName)

        #Preprocess the excel file and convert to csv
        dir = os.path.dirname(__file__)
        df = pd.DataFrame(pd.read_excel(file.filename))
        df = dropNameColumn(df)
        df = combineRaceAndEthnicity(df)
        df = reformatYearsColumn(df)
        df = formatData(df)
        destinationPath = os.path.join(dir, newFileName)
        if os.path.exists(destinationPath):
            os.unlink(destinationPath)
        df.to_csv(destinationPath, index=False)

        #save the csv file to datasets directory
        shutil.copy2(newFileName, destination)

        #Remove files from main directory
        os.remove(newFileName)
        os.remove(file.filename)


    return render_template('uploadDataset.html')

@login_required
@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    return render_template('createGraph.html')

if __name__ == "__main__":
    app.run(debug=True)