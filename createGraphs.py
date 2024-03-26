from appConfig import *

dir = os.path.dirname(__file__)
path = os.path.join(dir,'static', 'datasets', 'current.csv')
df = pd.read_csv(path)

def singleCategoryGraph(type, columnName, fileName):
    dict = df[columnName].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    otherCount = 0
    otheredRows = []
    for i, val in enumerate(vals):
        num = int(val)
        if num < OTHER_MIN_COUNT or ((len(df) - num) / len(df)) > (100 - OTHER_MIN_PERCENT) / 100:
            otherCount += num
            otheredRows.append(i)

    otheredRows.reverse()
    for i in otheredRows:
        del vals[i]
        del keys[i]
 
    if (otherCount > 0):
        keys.append("Other")
        vals.append(otherCount)
    
    fig, ax = plt.subplots() 
    match (type):
        case "pie":
            xLoc = 1
            yLoc = 0.5 if columnName != 'Department' else 0.15
            explode = [0.01 for _ in range(len(keys))]
            ax.pie(vals, autopct='%1.1f%%', explode=explode)
            plt.legend(keys, loc=(xLoc, yLoc), bbox_transform=plt.gcf().transFigure)
            plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0)
            plt.title("% of Employees per " + columnName)
        case "treemap":
            for i, key in enumerate(keys):
                keys[i] = key + "\n" + "{:1.1f}".format((1-(len(df) - vals[i]) / len(df))*100) + "%"
            squarify.plot(vals, label=keys)    
            plt.axis("off")
            plt.title("% of Employees per " + columnName)
        case "bar":
            plt.bar(keys, vals)
            plt.xlabel(columnName)
            plt.ylabel("# of Employees")
            plt.title("# of Employees per " + columnName)
    


    path = os.path.join(dir, 'static', 'graphs', fileName)
    fig.savefig(path, bbox_inches="tight")

def histogram(columnName, fileName):
    unsortedDict = df[columnName].value_counts().to_dict()
    keysMax = max(list(unsortedDict.keys()))
    keysMin = min(list(unsortedDict.keys()))
    for i in range(keysMax+1):
        if (i not in unsortedDict.keys()):
            unsortedDict[i] = 0
    sortedDict = dict(sorted(unsortedDict.items()))
    keys = list(sortedDict.keys())
    vals = list(sortedDict.values())
    fig, axs = plt.subplots()
    axs.bar(keys, vals, width=1.0)
    plt.xlabel(columnName)
    plt.ylabel("# of Employees")
    plt.title("# of Employees per " + columnName)
    path = os.path.join(dir, 'static', 'graphs', fileName)
    fig.savefig(path, bbox_inches="tight")


def stackedBarChart(mainColumnName, secondaryColumnName, fileName):
    # get keys in main column
    # for each key:
        # go through each row in df looking for rows with key value in column
        # add to list
        # list should be of format ['key', val1, val2, ... , valn]
    #
    
    data = {
        'Labels': ['A', 'B', 'C', 'D'],
        'Colors': ['red', 'blue', 'green', 'orange']
    }
    df = pd.DataFrame(data)

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Convert colors to categorical
    colors = pd.Categorical(df['Colors'])

    # Plot stacked bars
    ax.bar(df['Labels'], 1, color=colors)

    # Create legend from colors
    handles = [plt.Rectangle((0,0),1,1, color=color) for color in colors.categories]
    ax.legend(handles, colors.categories)

    # Set labels and title
    ax.set_xlabel('Labels')
    ax.set_ylabel('Value')
    ax.set_title('Stacked Bar Chart')
    path = os.path.join(dir, 'static', 'graphs', fileName)
    fig.savefig(path, bbox_inches="tight")

    None