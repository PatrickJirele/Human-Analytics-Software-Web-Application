import pandas as pd 
from random import randint
from datetime import datetime, timedelta
import os

excelMode = True
excelFileName = 'data.xlsx'
csvFileName = 'data.csv'

raceEthDict = {
    'A': 1,
    'B': 1,
    'H': 1,
    'I': 1,
    'P': 1,
    'S': 1,
    'U': 1,
    'W': 1
}

genderDict = {
    'F': 1,
    'M': 1,
    'Non Binary': 1,
    'Not Declared': 1    
}

employeeDict = {
    'Professional': 1,
    'Academic': 1,
    'State Classified': 1
}

nameDict = {
    'John': 1,
    'Joe': 1,
    'Jack': 1,
    'Jerry': 1,
    "Jason": 1,
    "Jamie": 1,
    "Jasmine": 1
}

def generateString(dict):
    combinedDict = {};
    maxVal = 0
    for key, val in dict.items():
        maxVal += val
        combinedDict[key] = maxVal
    num = randint(0,maxVal)
    
    for key,val in combinedDict.items():
        if (combinedDict[key] >= num):
            return key
    return "N/A"
    
def generateDate():
    num = randint(0, 5000)
    date = datetime.now() - timedelta(days=num)
    return date.strftime("%m/%d/%Y")

 
if __name__ == "__main__":
    df = pd.DataFrame(columns=["Name","Race/Ethnicity", "Gender", "Employee Type", "Years At Western"])
    for i in range(500):
        df.loc[i] = [generateString(nameDict),generateString(raceEthDict), generateString(genderDict), generateString(employeeDict), generateDate()]
    
    try:
        fileName = excelFileName if excelMode else csvFileName
        dir = os.path.dirname(__file__)
        path = os.path.join(dir, fileName)
        if os.path.exists(path):
            os.unlink(path)
        if (excelMode):
            df.to_excel(path, index=False)
        else:
            df.to_csv(path, index=False)
    except Exception as e:
        print("FAILED TO CREATE FILE")
        print(e)