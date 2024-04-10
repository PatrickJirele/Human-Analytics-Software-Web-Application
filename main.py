from appConfig import *
from preprocess import *
from createGraphs import *

# ____GLOBAL_VARIABLES_START____

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
login_manager.init_app(app)
db = SQLAlchemy(app)

cipher = SimpleCrypt()
cipher.init_app(app)

# ____GLOBAL_VARIABLES_END____

# ____CLASSES_START____

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)


class GraphGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100))
    graphs = db.relationship('Graphs', backref='GraphGroup')

class Graphs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('graph_group.id'), nullable=True)




# ____CLASSES_END____


# ____HELPER_FUNCTIONS_START____

#RETURNS all csv files from datasets dir AND all files from the annualDatasets dir
def getDatasets():
    dataset_files = [f for f in os.listdir('./static/datasets') if f.endswith('.csv')]
    annual_files = [f for f in os.listdir('./static/datasets/annualDatasets')]
    return dataset_files, annual_files

#RETURNS all graphs AND all currently displayed graphs
def getImgs():
    images = [f for f in os.listdir('./static/graphs') if os.path.isfile(os.path.join('./static/graphs', f))] #Sends all images in graphs to uploadGraphs.html
    selected = [f for f in os.listdir('./static/currentlyDisplayed') if os.path.isfile(os.path.join('./static/currentlyDisplayed', f))] #sends currently displayed imaged to uploadGraphs.html
    return images, selected

#Validates if entered email is in correct format
def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        print("Valid")
        return True
    else:
        print("Invalid")
        return False

# Returns all selected categories for pie, treemap, and bar charts.
def getSingleCategories(request):
    categories = []
    categories.append('Time Type') if (request.form.get('timeType')) else None
    categories.append('Job Family') if (request.form.get('jobFamily')) else None
    categories.append('Department') if (request.form.get('department')) else None
    categories.append('Race Ethnicity') if (request.form.get('raceEthnicity')) else None
    categories.append('Gender') if (request.form.get('gender')) else None
    return categories

# Returns all selected categories for histogram charts.
def getHistogramCategories(request):
    categories = []
    categories.append('Years At Western') if (request.form.get('yearsAtWestern')) else None
    categories.append('Age') if (request.form.get('age')) else None
    print(request.form)
    return categories

# Sets the name that will be used for chart image files.
def makeImageName(category, type, isUnique):
    return category + "_" + type + ("_" + datetime.now().strftime("%m_%d_%Y_%H;%M;%S") + ".png" if isUnique else ".png")

def addGraphToDb(path, title, description="", group_id=None):
    if group_id == None:
        temp = Graphs(path=path, title=title, description=description)
    else:
        temp = Graphs(path=path, title=title, description=description, group_id=None)

    print(title + "\n")
    checker = Graphs.query.filter_by(title=title).first()
    if checker != None:
        print("graph with same name is in db already\n\n")
    else:
        db.session.add(temp)
        db.session.commit()
        print("graph uploaded to database")

    return(exit(1))



# ____HELPER_FUNCTIONS_END____


# ____ROUTES_START____

@app.route('/')
def home():
    _, graphsToDisplay = getImgs()
    return render_template('home.html', graphs=graphsToDisplay)


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
        db.session.commit()
        return flask.redirect('/')
    return render_template('updatePassword.html')

@login_required
@app.route('/createAdmin', methods = ['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form['email']
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
    dataset_files, annual_files = getDatasets()
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
            df = removeNaN(df)
            df = combineRaceAndEthnicity(df)
            df = reformatYearsColumn(df)
            df = modifyName(df, "Race/Ethnicity")
            destinationPath = os.path.join(dir, newFileName)
            if os.path.exists(destinationPath):
                os.unlink(destinationPath)
            df.to_csv(destinationPath, index=False)

            # Save the csv file to datasets directory
            shutil.copy2(newFileName, destination)
            # Make a current copy to use as the current dataset
            shutil.copy2(destinationPath, os.path.join(destination, 'current.csv'))
            if 'annual_dataset' in request.form:
                isAnnual = request.form['annual_dataset']
                if isAnnual == 'on':
                    annualPath = './static/datasets/annualDatasets'
                    shutil.copy2(destinationPath, os.path.join(annualPath, str(date.today().year)+'.csv'))
            
            # Remove files from main directory
            os.remove(newFileName)
            os.remove(file.filename)
            dataset_files, annual_files = getDatasets()
            
    return render_template('uploadDataset.html', dataset_files=dataset_files, annual_files=annual_files)


@login_required
@app.route('/deleteDataset', methods=['POST'])
def delete_file():
    filename = request.json['filename']
    normal_file_path = os.path.join('./static/datasets', filename)
    annual_file_path = os.path.join('./static/datasets/annualDatasets', filename)
    file_path = normal_file_path if os.path.exists(normal_file_path) else annual_file_path

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'File not found'})

@login_required
@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    if request.method == "POST":
        try:
            chartType = request.form.get('chartType')
            if (chartType == 'pie' or chartType =='treemap' or chartType == 'bar'):
                categories = getSingleCategories(request)
                for category in categories:
                    imageName = makeImageName(category, chartType, ("overwrite" in request.form))
                    singleCategoryGraph(chartType, category, imageName)
            if (chartType == 'histogram'):
                categories = getHistogramCategories(request)
                for category in categories:
                    imageName = makeImageName(category, chartType, ("overwrite" in request.form))
                    histogram(category, imageName)
            if (chartType == 'stackedBar'):
                primaryCategory = request.form.get('primary')
                secondaryCategory = request.form.get('secondary')
                imageName = makeImageName(primaryCategory+"_"+secondaryCategory, chartType, ("overwrite" in request.form))
                stackedBarChart(primaryCategory, secondaryCategory, imageName)
            addGraphToDb(path="./static/graphs", title=imageName, description="TEST")
            return redirect("/uploadGraphs")
        except Exception as e:
            print(traceback.format_exc())
    return render_template('createGraph.html')

@login_required
@app.route("/uploadGraphs", methods = ['GET', 'POST'])
def selectGraphsForDashboard():
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
        flash('Graphs selected successfully', 'success')
        return flask.redirect('/uploadGraphs')
        #return render_template('uploadGraphs.html', images=updated_Images, selected = updated_Selected)
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

# ____ROUTES_END____

if __name__ == "__main__":
    app.run(debug=True)