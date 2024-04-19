from appConfig import *
from preprocess import *
from createGraphs import *

# ____GLOBAL_VARIABLES_START____

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
login_manager = LoginManager(app)
"""
login view used to redirect unauthorized users from private routes
"""
login_manager.login_view = '/'
login_manager.login_message = ''
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
    authenticated = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return  True

    def get_id(self):
        return  self.id

    def is_anonymous(self):
        return False


class GraphGroup(db.Model):
    __tablename__ = 'graphgroup'
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100))
    currently_displayed = db.Column(db.Boolean, default=False, nullable=False)
    graphs = db.relationship('Graphs', backref='GraphGroup', lazy='dynamic')

class Graphs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    type = db.Column(db.String(20))
    currently_displayed = db.Column(db.Boolean, default=False, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('graphgroup.id'), nullable=True)


# ____CLASSES_END____


# ____HELPER_FUNCTIONS_START____

#RETURNS all csv files from datasets dir
def getDatasets():
    dataset_files = [f for f in os.listdir('./static/datasets') if f.endswith('.csv')]
    return dataset_files


#RETURNS all graphs AND all currently displayed graphs
def getImgs():
    images = [f for f in os.listdir('./static/graphs') if
              os.path.isfile(os.path.join('./static/graphs', f))]  #Sends all images in graphs to uploadGraphs.html
    selected = [f for f in os.listdir('./static/currentlyDisplayed') if os.path.isfile(
        os.path.join('./static/currentlyDisplayed', f))]  #sends currently displayed imaged to uploadGraphs.html

    return images, selected



#Validates if entered email is in correct format
def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if (re.fullmatch(regex, email)):
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


def addGraphToDb(path, title, type, description="", group_id=None):
    if group_id == None:
        temp = Graphs(path=path, title=title, type=type, description=description)
    else:
        temp = Graphs(path=path, title=title, type=type, description=description, group_id=None)

    print(title + "\n")
    checker = Graphs.query.filter_by(path=path).first()
    if checker != None:
        db.session.delete(checker)
        db.session.add(temp)
        db.session.commit()
    else:
        db.session.add(temp)
        db.session.commit()

def getGraphsFromDb(listOfGraphs):
    retList = []
    for graph in listOfGraphs:
        graphPath = './static/graphs/'+graph
        retList.append(Graphs.query.filter_by(path=graphPath).first())
    return retList


def regenerateGraphs():
    dataset_path = './static/datasets/current.csv'
    images, selected = getImgs()
    split_images = [item[:-4].split('_') for item in images]
    for i, img in enumerate(split_images):
        graph = Graphs.query.filter_by(path = ("./static/graphs/" + images[i])).first()
        title = graph.title
        type= img[-1]
        print({'IMG: ' : img, 'TYPE: ' : img[-1]})
        if type == 'stackedBar':
            columnName1 = img[0]
            columnName2 = img[1]
            imageName = makeImageName(columnName1 + "_" + columnName2, type, False)
            stackedBarChart(columnName1, columnName2, imageName, title, False)
        else:
            columnName1 = img[0]
            if type == 'pie' or type == 'treemap' or type == 'bar':
                imageName = makeImageName(columnName1, type, False)
                singleCategoryGraph(type, columnName1, imageName, title, False)
            if type == 'histogram':
                imageName = makeImageName(columnName1, type, False)
                histogram(columnName1, imageName, title, False)

# ____HELPER_FUNCTIONS_END____


# ____ROUTES_START____

@app.route('/')
def home():
    graphsFromDb = Graphs.query.filter_by(currently_displayed = 1).all()
    graphs_by_group = GraphGroup.query.filter_by(currently_displayed = 1).all()

    return render_template('home.html', graphs=graphsFromDb, graphGroups = graphs_by_group)

@app.route('/filterGraphs', methods=['GET', 'POST'])
def filterGraphs():
    graphsOfType = None
    graphsOfField = None
    retGraphs = []
    typeSelected = ""
    fieldSelected = ""
    messageToSend = ""
    if request.method == "POST":
        if request.form["graphType"]:
            typeSelected = request.form["graphType"]
            graphsOfType = Graphs.query.filter(Graphs.type.like(typeSelected)).all()

        if request.form["graphField"]:
            fieldSelected = request.form["graphField"]
            graphField = "%{}%".format(fieldSelected)
            graphsOfField = Graphs.query.filter(Graphs.path.like(graphField)).all()

        if graphsOfType != None and graphsOfField != None:
            for graphOfType in graphsOfType:
                for graphOfField in graphsOfField:
                    if graphOfField == graphOfType:
                        retGraphs.append(graphOfField)
            if len(retGraphs) == 0:
                retGraphs = None
                messageToSend='No matches found of graph type('+typeSelected+') and graph field('+fieldSelected+')'
            else:
                messageToSend='Graphs Found from selected field('+fieldSelected+') and selected graph type('+typeSelected+'): '

        if graphsOfType != None and graphsOfField == None:
            messageToSend='Graphs Available from selected type('+typeSelected+'):'
            retGraphs = graphsOfType

        if graphsOfType == None and graphsOfField != None:
            messageToSend='Graphs Available from selected field('+fieldSelected+'): '
            retGraphs = graphsOfField

        return render_template('filterGraphs.html', graphs=retGraphs, message=messageToSend)

    return render_template('filterGraphs.html')

@app.route('/login', methods=['GET', 'POST'])
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
                    user.authenticated = True
                    db.session.add(user)
                    db.session.commit()
                    login_user(user, remember=True)
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
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return flask.redirect('/')


@app.route('/updatePassword', methods=['GET', 'POST'])
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


@app.route('/createAdmin', methods=['GET', 'POST'])
@login_required
def create():
    admins = User.query.filter(User.admin != 1).all()
    print(admins)
    if request.method == 'POST':
        email = request.form['email']
        password = cipher.encrypt(request.form['pWord'])
        if check(email) == False:
            return render_template('createAdmin.html'), 'Invalid Email Address'
        temp = User(email=email, password=password)
        user = User.query.filter_by(email=request.form['email']).first()
        if user != None:
            return render_template('createAdmin.html'), 'user already exists'
        else:
            db.session.add(temp)
            db.session.commit()
            # user = User.query.filter_by(email=request.form['email']).first()
            # login_user(user)
            return flask.redirect('/createAdmin')

    return render_template('createAdmin.html', admins=admins)


@app.route('/uploadDataset', methods=['GET', 'POST'])
@login_required
def uploadDataset():
    try:
        failure = None
        dataset_files = getDatasets()
        selected_dataset = request.args.get('filename', 'None')
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

                # Remove files from main directory
                os.remove(newFileName)
                os.remove(file.filename)
                dataset_files = getDatasets()
    except Exception as e:
        failure = "Failed to upload new data. Please close Excel if open and ensure new data is valid."
    return render_template('uploadDataset.html', dataset_files=dataset_files, selected_dataset=selected_dataset, failure=failure)

@app.route('/deleteDataset', methods=['POST'])
@login_required
def delete_file():
    filename = request.json['filename']
    normal_file_path = os.path.join('./static/datasets', filename)
    file_path = normal_file_path if os.path.exists(normal_file_path) else ""

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'File not found'})

@app.route("/selectDataset/<filename>", methods=["GET"])
@login_required
def selectDataset(filename):
    normal_file_path = os.path.join('./static/datasets', filename)
    file_path = normal_file_path if os.path.exists(normal_file_path) else ""

    if os.path.exists(file_path):
        # right here is where we change the graphs and everything
        # Make a current copy to use as the current dataset
        dir = os.path.dirname(__file__)
        destination = './static/datasets'
        destinationPath = os.path.join(dir, destination, filename)
        shutil.copy2(destinationPath, os.path.join(destination, 'current.csv'))

        regenerateGraphs()
        # Redirect to the home page or the page where the graphs are displayed
        return jsonify({'success': True, 'filename': filename})
    else:
        print("File path does not exist:", file_path)
        return jsonify({'success': False, 'error': 'File not found'})

@login_required
@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    if request.method == "POST":
        try:
            chartType = request.form.get('chartType')
            dbTitle = request.form.get('title')
            useQuantity = ("quantity" in request.form)
            unique = (("overwrite" not in request.form) and useQuantity)
            dbDescription = ""
            if (chartType == 'pie' or chartType =='treemap' or chartType == 'bar'):
                category = request.form.get('singleCategory')
                imageName = makeImageName(category, chartType, unique)
                dbDescription = singleCategoryGraph(chartType, category, imageName, dbTitle, useQuantity)
            if (chartType == 'histogram'):
                category = request.form.get('histCategory')
                imageName = makeImageName(category, chartType, unique)
                dbDescription = histogram(category, imageName, dbTitle, useQuantity)
            if (chartType == 'stackedBar'):
                primaryCategory = request.form.get('primary')
                secondaryCategory = request.form.get('secondary')
                imageName = makeImageName(primaryCategory+"_"+secondaryCategory, chartType, unique)
                dbDescription = stackedBarChart(primaryCategory, secondaryCategory, imageName, dbTitle, useQuantity)
            dbTitle = dbTitle if not dbTitle == "" else imageName.replace('.png', '')
            addGraphToDb(path="./static/graphs/"+imageName, title=dbTitle, description=dbDescription, type=chartType)
            return redirect("/uploadGraphs")
        except Exception as e:
            print(traceback.format_exc())
    return render_template('createGraph.html')

@app.route("/uploadGraphs", methods=['GET', 'POST'])
@login_required
def selectGraphsForDashboard():
    graphs = Graphs.query.all()
    return render_template('uploadGraphs.html', graphs=graphs)

@app.route('/deleteGraph/<graph_id>', methods=['DELETE'])
@login_required
def deleteGraph(graph_id):
    print(graph_id)
    try:
        graphToDelete = Graphs.query.filter_by(id=graph_id).first()
        print(graphToDelete)
        print(graphToDelete.path)
        os.remove(graphToDelete.path)
        db.session.delete(graphToDelete)
        db.session.commit()
        return jsonify({'message': 'Graph deleted successfully'}), 200
    except:
        return jsonify({'message': 'Error deleting graph'}), 500


@app.route('/editGraph/<imgName>', methods=['GET', 'POST'])
@login_required
def editGraph(imgName):
    graphDir = './static/graphs/' + imgName
    graphToEdit = Graphs.query.filter_by(path=graphDir).first()

    if request.method == 'POST':
        graphToEdit.title = request.form['title']
        graphToEdit.description = request.form['description']
        db.session.commit()
        return redirect('/uploadGraphs')

    return render_template('editGraph.html', graphToEdit=graphToEdit)


@app.route('/displayGraph/<graph_id>', methods=['DISPLAY'])
@login_required
def displayGraph(graph_id):
    try:
        group = Graphs.query.filter_by(id=graph_id).first()
        group.currently_displayed = 1
        db.session.add(group)
        db.session.commit()
        return jsonify({'message': 'Group displayed successfully'}), 200
    except:
        return jsonify({'message': 'Error displaying group'}), 500


@app.route('/removeDisplayGraph/<graph_id>', methods=['REMOVE'])
@login_required
def removeDisplayGraph(graph_id):
    try:
        group = Graphs.query.filter_by(id=graph_id).first()
        group.currently_displayed = 0
        db.session.add(group)
        db.session.commit()
        return jsonify({'message': 'Group displayed successfully'}), 200
    except:
        return jsonify({'message': 'Error displaying group'}), 500

@app.route('/updateGraphInfo/<graph_id>', methods=['POST'])
@login_required
def updateGraphInfo(graph_id):
    graph = Graphs.query.filter_by(id=graph_id).first()
    new_title = request.form['new_title']
    new_description = request.form['new_description']
    graph.title= new_title
    graph.description = new_description
    db.session.add(graph)
    db.session.commit()
    return redirect('/uploadGraphs')


@app.route("/editGroups", methods=['GET', 'POST'])
@login_required
def editGroups():
    graphs_by_group = GraphGroup.query.all()

    available_graphs = Graphs.query.filter(~Graphs.id.in_(
        db.session.query(Graphs.id)
        .join(Graphs.GraphGroup)
        .filter(GraphGroup.id == GraphGroup.id)
    )).all()

    return render_template('editGroups.html', graphGroups=graphs_by_group, available_graphs=available_graphs)


@app.route('/add-graph-to-group/<group_id>', methods=['POST'])
@login_required
def add_graph_to_group(group_id):
    graph_id = request.form['available_graphs']
    graph = Graphs.query.get(graph_id)
    group = GraphGroup.query.get(group_id)
    group.graphs.append(graph)
    db.session.commit()
    return redirect('/editGroups')


@app.route('/update-group-name/<group_id>', methods=['POST'])
@login_required
def update_group_name(group_id):
    group = GraphGroup.query.get(group_id)
    new_name = request.form['new_name']
    group.group_name = new_name
    db.session.commit()
    return redirect('/editGroups')

@app.route('/remove-graph', methods=['REMOVE'])
@login_required
def remove_graph():
    graph_id = request.args.get('graph_id')
    group_id = request.args.get('group_id')

    graph = Graphs.query.get(graph_id)
    graph.group_id = None
    db.session.commit()
    return '', 204

@app.route('/createGroup', methods=['POST'])
@login_required
def createGroup():
    new_group_name = request.form['new_group_name']
    new_group = GraphGroup(group_name=new_group_name)
    db.session.add(new_group)
    db.session.commit()
    return redirect('/editGroups')


@app.route('/deleteGroup/<group_id>', methods=['DELETE'])
@login_required
def deleteGroup(group_id):
    print(group_id)
    try:
        db.session.delete(GraphGroup.query.get(group_id))
        db.session.commit()
        return jsonify({'message': 'Group deleted successfully'}), 200
    except:
        return jsonify({'message': 'Error deleting group'}), 500



@app.route('/displayGroup/<group_id>', methods=['DISPLAY'])
@login_required
def displayGroup(group_id):
    print(group_id)
    try:
        group = GraphGroup.query.filter_by(id=group_id).first()
        group.currently_displayed = 1
        db.session.add(group)
        db.session.commit()
        return jsonify({'message': 'Group displayed successfully'}), 200
    except:
        return jsonify({'message': 'Error displaying group'}), 500

@app.route('/removeDisplayGroup/<group_id>', methods=['REMOVE'])
@login_required
def removeDisplayGroup(group_id):
    print(group_id)
    try:
        group = GraphGroup.query.filter_by(id=group_id).first()
        group.currently_displayed = 0
        db.session.add(group)
        db.session.commit()
        return jsonify({'message': 'Group displayed successfully'}), 200
    except:
        return jsonify({'message': 'Error displaying group'}), 500


@app.route('/deleteAdmin/<user_id>', methods=['DELETE'])
@login_required
def deleteAdmin(user_id):
    try:
        results = User.query.filter_by(id=user_id).first()
        db.session.delete(results)
        db.session.commit()
        return jsonify({'message': 'Admin deleted successfully'}), 200
    except:
        return jsonify({'message': 'Error deleting admin'}), 500




# ____ROUTES_END____

if __name__ == "__main__":
    app.run(debug=True)
