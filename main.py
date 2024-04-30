from appConfig import *
from preprocess import *
from createGraphs import *

# ____GLOBAL_VARIABLES_START____

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usersDB.db'
app.config['SECRET_KEY'] = 'secretKey'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
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
    useQuantity = db.Column(db.Boolean, default=False)
    currently_displayed = db.Column(db.Boolean, default=False, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('graphgroup.id'), nullable=True)


# ____CLASSES_END____


# ____HELPER_FUNCTIONS_START____

#RETURNS all csv files from datasets dir
def getDatasets():
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'static', 'datasets')
    dataset_files = [f for f in os.listdir(path) if f.endswith('.csv')]

    # dataset_files = [f for f in os.listdir('./static/datasets') if f.endswith('.csv')]
    return dataset_files


#RETURNS all graphs AND all currently displayed graphs
def getImgs():
    graphsPath = os.path.dirname(__file__)
    # images = [f for f in os.listdir('./static/graphs') if
    #           os.path.isfile(os.path.join('./static/graphs', f))]  #Sends all images in graphs to uploadGraphs.html
    images = [f for f in os.listdir(graphsPath) if
              os.path.isfile(os.path.join(graphsPath, f))]  #Sends all images in graphs to uploadGraphs.html
    return images



#Validates if entered email is in correct format
def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if (re.fullmatch(regex, email)):
        return True
    else:
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
    return categories


# Sets the name that will be used for chart image files.
def makeImageName(category, type, isUnique):
    return category + "_" + type + ("_" + datetime.now().strftime("%m_%d_%Y_%H;%M;%S") + ".png" if isUnique else ".png")



def addGraphToDb(path, title, type, description="", group_id=None, useQuantity=False):
    if group_id == None:
        temp = Graphs(path=path, title=title, type=type, description=description, useQuantity=useQuantity)
    else:
        temp = Graphs(path=path, title=title, type=type, description=description, group_id=None, useQuantity=useQuantity)

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
        #graphPath = './static/graphs/'+graph
        dir = os.path.dirname(__file__)
        graphPath = os.path.join(dir, 'static', 'graphs', graph)

        retList.append(Graphs.query.filter_by(path=graphPath).first())
    return retList


def regenerateGraphs(specificGraph = None):
    dataset_path = './static/datasets/current.csv'

    graphs = Graphs.query.all() if specificGraph == None else specificGraph
    for graph in graphs:
        img = graph.path.replace('static/graphs/', '')[:-4].split('_')
        type= img[-1]
        title = graph.title
        description = None
        useQuantity = graph.useQuantity
        if type == 'Stacked Bar' or type == 'Treemap':
            columnName1 = img[0]
            columnName2 = img[1]
            imageName = makeImageName(columnName1 + "_" + columnName2, type, False)
            if (type == 'Stacked Bar'):
                description = stackedBarChart(columnName1, columnName2, imageName, title, useQuantity)
            else:
                description = treemap(columnName1, columnName2, imageName, title, useQuantity)
        else:
            columnName1 = img[0]
            if type == 'Pie' or type == 'Bar':
                imageName = makeImageName(columnName1, type, False)
                description = singleCategoryGraph(type, columnName1, imageName, title, useQuantity)
            if type == 'Histogram':
                imageName = makeImageName(columnName1, type, False)
                description = histogram(columnName1, imageName, title, useQuantity)

        graph.description = description
        db.session.add(graph)
        db.session.commit()



#For keeping track of the current.csv
#Returns the actual dataset name of current.csv
global currentCSV_name
currentCSV_name = 'current.csv'
def setCurrentDataset(dataset):
    globals()['currentCSV_name'] = dataset



# ____HELPER_FUNCTIONS_END____


# ____ROUTES_START____

@app.route('/')
def home():
    graphsFromDb = Graphs.query.filter_by(currently_displayed = 1).all()
    graphs_by_group = GraphGroup.query.filter_by(currently_displayed = 1).all()
    return render_template('home.html', graphs=graphsFromDb, graphGroups=graphs_by_group)

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
            retGraphs = graphsOfType
            if len(retGraphs) == 0:
                retGraphs = None
                messageToSend='No matches found of graph type('+typeSelected+')'
            else:
                messageToSend='Graphs Available from selected type('+typeSelected+'):'

        if graphsOfType == None and graphsOfField != None:
            retGraphs = graphsOfField
            if len(retGraphs) == 0:
                retGraphs = None
                messageToSend='No matches found of graph type('+fieldSelected+')'
            else:
                messageToSend='Graphs Available from selected field('+fieldSelected+'): '

        hasDisplayedGraphs = False
        if retGraphs != None:
            for graph in retGraphs:
                if (graph.currently_displayed == True):
                    hasDisplayedGraphs = True

        return render_template('filterGraphs.html', graphs=retGraphs, message=messageToSend, has_displayed_graphs = hasDisplayedGraphs)

    return render_template('filterGraphs.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if check(email) == True:
            user = User.query.filter_by(email=email).first()
            if user != None:
                userPass = (cipher.decrypt(user.password)).decode('utf-8')
                if request.form['pWord'] != userPass:
                    return render_template('login.html')
                else:
                    user.authenticated = True
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                    session.permanent = True
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
            return flask.redirect('/createAdmin')

    return render_template('createAdmin.html', admins=admins)


@app.route('/uploadDataset', methods=['GET', 'POST'])
@login_required
def uploadDataset():
    dataset_files = getDatasets()
    selected_dataset = request.args.get('filename', 'None')
    if request.method == 'POST':
        if request.files['file']:
            # Get the excel file from website upload
            file = request.files['file']
            dir = os.path.dirname(__file__)
            file.save(file.filename)
            #destination = './static/datasets'
            destination = os.path.join(dir, 'static', 'datasets')
            newFileName = str(date.today()) + '.csv'
            destinationPath = os.path.join(dir, newFileName)
            if os.path.isfile(destinationPath):
                os.remove(destinationPath)
            """
            if os.path.isfile(newFileName):
                os.remove(newFileName)
            """
            # Preprocess the excel file and convert to csv
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
            #shutil.copy2(newFileName, destination)
            shutil.copy2(destinationPath, destination)

            # Make a current copy to use as the current dataset
            shutil.copy2(destinationPath, os.path.join(destination, 'current.csv'))

            # Remove files from main directory

            #os.remove(newFileName)
            #os.remove(file.filename)
            os.remove(destinationPath)
            os.remove(os.path.join(dir, '..', file.filename))
            dataset_files = getDatasets()
            setCurrentDataset(newFileName)

    return render_template('uploadDataset.html', dataset_files=dataset_files, selected_dataset=selected_dataset, current_dataset = currentCSV_name)

@app.route('/deleteDataset', methods=['POST'])
@login_required
def delete_file():
    filename = request.json['filename']

    # normal_file_path = os.path.join('./static/datasets', filename)
    dir = os.path.dirname(__file__)
    normal_file_path = os.path.join(dir, 'static', 'datasets', filename)

    file_path = normal_file_path if os.path.exists(normal_file_path) else ""

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'File not found'})

@app.route("/selectDataset/<filename>", methods=["GET"])
@login_required
def selectDataset(filename):
    dir = os.path.dirname(__file__)
    # normal_file_path = os.path.join('./static/datasets', filename)
    normal_file_path = os.path.join(dir, 'static', 'datasets', filename)

    file_path = normal_file_path if os.path.exists(normal_file_path) else ""

    if os.path.exists(file_path):
        # Right here is where we change the graphs and everything
        # Make a current copy to use as the current dataset
        dir = os.path.dirname(__file__)
        #destination = './static/datasets'
        #destinationPath = os.path.join(dir, destination, filename)
        destination = os.path.join(dir, 'static', 'datasets')
        destinationPath = os.path.join(destination, filename)

        shutil.copy2(destinationPath, os.path.join(destination, 'current.csv'))
        regenerateGraphs()
        setCurrentDataset(filename)

        # Redirect to the home page or the page where the graphs are displayed
        return jsonify({'success': True, 'filename': filename})
    else:
        return jsonify({'success': False, 'error': 'File not found'})

@login_required
@app.route('/createGraph', methods = ['GET', 'POST'])
def createGraph():
    if request.method == "POST":
        try:
            chartType = request.form.get('chartType')
            dbTitle = request.form.get('title')
            useQuantity = ("quantity" in request.form)
            dbDescription = ""
            imageName = None
            if (chartType == 'Pie' or chartType == 'Bar'):
                category = request.form.get('singleCategory')
                imageName = makeImageName(category, chartType, ("overwrite" not in request.form))
                dbDescription = singleCategoryGraph(chartType, category, imageName, dbTitle, useQuantity)
            if (chartType == 'Histogram'):
                category = request.form.get('histCategory')
                imageName = makeImageName(category, chartType, ("overwrite" not in request.form))
                dbDescription = histogram(category, imageName, dbTitle, useQuantity)
            if (chartType == 'Stacked Bar'):
                primaryCategory = request.form.get('primary')
                secondaryCategory = request.form.get('secondary')
                imageName = makeImageName(primaryCategory+"_"+secondaryCategory, chartType, ("overwrite" not in request.form))
                dbDescription = stackedBarChart(primaryCategory, secondaryCategory, imageName, dbTitle, useQuantity)
            if (chartType == 'Treemap'):
                primaryCategory = request.form.get('primaryTree')
                secondaryCategory = request.form.get('secondaryTree')
                imageName = makeImageName(primaryCategory+"_"+secondaryCategory, chartType, ("overwrite" not in request.form))
                dbDescription = treemap(primaryCategory, secondaryCategory, imageName, dbTitle, useQuantity)
            dbTitle = dbTitle if not dbTitle == "" else imageName.replace('.png', '')
            imagePath = os.path.join('static', 'graphs', imageName)
            addGraphToDb(path=imagePath, title=dbTitle, description=dbDescription, type=chartType, useQuantity=useQuantity)
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
    try:
        graphToDelete = Graphs.query.filter_by(id=graph_id).first()
        file_path = graphToDelete.path
        dir = os.path.dirname(__file__)
        file_path = os.path.join(dir, file_path)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                db.session.delete(graphToDelete)
                db.session.commit()
                return jsonify({'message': 'Graph deleted successfully'}), 200
            except OSError as e:
                print(f"Error deleting file: {e}")
                return jsonify({'message': 'Error deleting graph file'}), 500
        else:
            print("File not found")
            return jsonify({'message': 'Graph file not found'}), 404

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': 'Error deleting graph'}), 500



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
        return jsonify({'message': 'Graph displayed successfully'}), 200
    except:
        return jsonify({'message': 'Error displaying graph'}), 500


@app.route('/updateGraphInfo/<graph_id>', methods=['POST'])
@login_required
def updateGraphInfo(graph_id):
    graph = Graphs.query.filter_by(id=graph_id).first()
    new_title = request.form['new_title']
    new_description = request.form['new_description']
    graph.title= new_title
    regenerateGraphs([graph])
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
    try:
        db.session.delete(GraphGroup.query.get(group_id))
        db.session.commit()
        return jsonify({'message': 'Group deleted successfully'}), 200
    except:
        return jsonify({'message': 'Error deleting group'}), 500



@app.route('/displayGroup/<group_id>', methods=['DISPLAY'])
@login_required
def displayGroup(group_id):
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
