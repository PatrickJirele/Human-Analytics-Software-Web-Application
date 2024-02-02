import flask
from flask import *
from flask_sqlalchemy import *
from flask_login import LoginManager, UserMixin, login_user, \
    logout_user, current_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'secret-key'
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(80))
    password = db.Column(db.String(80))


app.config['SECRET KEY'] = 'Secret-Key'
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(uid):
    user = Users.query.get(uid)
    return user
@app.route('/')
def home():
    login = False
    return render_template('home.html', login=login)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(userName=userName).first()

        if userName != user.userName or password != user.password:
            uniqueName = False
            return render_template('login.html', uniqueName=uniqueName)

        global id
        id = user.id

        login_user(user)
        login = True
        return render_template('home.html', login=login)

    elif request.method == 'GET':
        uniqueName = True
        return render_template('login.html')

if __name__ == '__main__':
    app.run()
