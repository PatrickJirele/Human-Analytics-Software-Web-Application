from appConfig import *
from preprocess import *

# GLOBAL VARIABLES - START

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
login_manager.init_app(app)
db = SQLAlchemy(app)

cipher = SimpleCrypt()
cipher.init_app(app)

# GLOBAL VARIABLES - END


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

#Validates if entered email is in correct format
#Validates if entered email is in correct format
def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        print("Valid")
        return True
    else:
        print("Invalid")
        return False




def createGraphsFromDict(df, dictionary):
    for column_key in dictionary.keys():
        for queries in dictionary[column_key]:
            total_population = len(df[column_key])
            true_rows = len(df[df[column_key] == queries])

            labels = ['True Population', 'Total Population']
            sizes = [true_rows, total_population - true_rows]
            colors = ['#ff9999', '#66b3ff']
            explode = (0.1, 0)
            fig, ax = plt.subplots()
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            ax.set_title(f'True Population vs Total Population for Query: {queries}')

            column_name = modifyName(column_key)
            todaysdate = date.today()
            fileName = f'{column_name}_{queries}_{todaysdate}.png'

            dir = os.path.dirname(__file__)
            path = os.path.join(dir, 'static')
            path = os.path.join(path, 'graphs')
            path = os.path.join(path, fileName)
            fig.savefig(path)

            plt.show()
            plt.close()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if check(email) == True:
            user = User.query.filter_by(email=email).first()
            userPass = (cipher.decrypt(user.password)).decode('utf-8')
            if user != None:
                if request.form['pWord'] != userPass:
                    return render_template('login.html')
                else:
                    login_user(user)
                    return flask.redirect('/')
            return render_template('login.html')
        else:
            return render_template('login.html')
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
        if cipher.decrypt(current_user.password) != oldPassword:
            return render_template('updatePassword.html')
        updatedUser = User.query.filter_by(id=current_user.id).first()
        updatedUser.password = cipher.encrypt(request.form['newP'])
        #updatedUser.password = request.form['newP']
        db.session.commit()
        return flask.redirect('/')
    return render_template('updatePassword.html')

@login_required
@app.route('/createAdmin', methods = ['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form['email']
        #password = request.form['pWord']
        password = cipher.encrypt(request.form['pWord'])
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
        if request.files['file']:
            # Get the excel file from website upload
            file = request.files['file']
            file.save(file.filename)
            destination = './static/datasets'
            newFileName = str(date.today()) + '.csv'
            if os.path.isfile(newFileName):
                os.remove(newFileName)

            # Preprocess the excel file and convert to csv
            dir = os.path.dirname(__file__)
            df = pd.DataFrame(pd.read_excel(file.filename))
            df = combineRaceAndEthnicity(df)
            df = reformatYearsColumn(df)
            destinationPath = os.path.join(dir, newFileName)
            if os.path.exists(destinationPath):
                os.unlink(destinationPath)
            df.to_csv(destinationPath, index=False)

            # save the csv file to datasets directory
            shutil.copy2(newFileName, destination)
            # make a current copy to use as the current dataset
            shutil.copy2(destinationPath, os.path.join(destination, 'current.csv'))
            if 'annual_dataset' in request.form:
                annualPath = './static/datasets/annualDatasets'
                shutil.copy2(destinationPath, os.path.join(annualPath, str(date.today().year)))
            
            # Remove files from main directory
            os.remove(newFileName)
            os.remove(file.filename)



    return render_template('uploadDataset.html')

@login_required
@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    return render_template('createGraph.html')

@login_required
@app.route("/uploadGraphs", methods = ['GET', 'POST'])
def selectGraphsForDashboard():
    def getImgs():
        images_dir = './static/graphs'
        selected_dir = './static/currentlyDisplayed'
        images = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))] #Sends all images in graphs to uploadGraphs.html
        selected = [f for f in os.listdir(selected_dir) if os.path.isfile(os.path.join(selected_dir, f))] #sends currently displayed imaged to uploadGraphs.html
        return images, selected

    images, selected = getImgs()


    if request.method == "POST":
        destination = './static/currentlyDisplayed'
        list_of_graphs = request.form.getlist('image_list[]')

        for graph in list_of_graphs:
            srcPath = os.path.join('./static/graphs', graph)
            shutil.copy2(srcPath, destination)

        _, selected_imgs = getImgs()
        for img in selected_imgs:
            if img not in list_of_graphs:
                img_to_rm = os.path.join(destination, img)
                os.remove(img_to_rm)

        updated_Images, updated_Selected = getImgs()
        return render_template('uploadGraphs.html', images=updated_Images, selected = updated_Selected)


    return render_template('uploadGraphs.html', images=images, selected = selected)

@login_required
@app.route('/deleteGraph/<imgName>', methods = ['GET', 'POST'])
def delete(imgName):
    if request.method == 'POST':
        graphDir = './static/graphs'
        currDir = './static/currentlyDisplayed'
        img_to_rm = os.path.join(graphDir, imgName)
        os.remove(img_to_rm)
        if os.path.isfile(os.path.join(currDir, imgName)):
            img_to_rm = os.path.join(currDir, imgName)
            os.remove(img_to_rm)
        return flask.redirect('/uploadGraphs')

    return flask.redirect('/uploadGraphs')

if __name__ == "__main__":
    app.run(debug=True)