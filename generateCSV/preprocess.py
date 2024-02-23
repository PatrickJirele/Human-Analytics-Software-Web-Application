import pandas as pd
from datetime import datetime
from dateutil import relativedelta
import os

# TO DO:
# Combine Race & Ethnicity


originalFileName = 'data.csv'
destinationFileName = 'preprocessed.csv'
maxNumberOfMissingCells = 2


# Format:
#   Spreadsheet Name: Displayed Name
#
# If displayed name = 1, spreadsheet name will be used as the displayed name.

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

def dropNameColumn(df):
    try:
        df = df.drop('Name', axis=1)
    except:
        print('Column "Name" does not exist.')
    return df

def combineRaceAndEthnicity(df):
    return df

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

def formatData(df):
    for columnName, values in [('Race/Ethnicity', raceEthDict), ('Gender',genderDict), ('Employee Type', employeeDict)]:
        formatDataPerColumn(df, columnName, values)
    df.dropna(thresh=maxNumberOfMissingCells, inplace = True);
    df.replace('', 'NaN', inplace = True)
    return df

def formatDataPerColumn(df, columnName, values):
    for i in range(len(df)):
        value = df.loc[i, columnName]
        if (value not in values):
            df.loc[i,columnName] = ''
        else:
            if (values[value] != 1):
                df.loc[i, columnName] = values[value]
    return df

     
dir = os.path.dirname(__file__)
originalPath = os.path.join(dir, originalFileName)
df = pd.read_csv(originalPath)
df = dropNameColumn(df)
df = combineRaceAndEthnicity(df)
df = reformatYearsColumn(df)
df = formatData(df)
destinationPath = os.path.join(dir, destinationFileName)
if os.path.exists(destinationPath):
    os.unlink(destinationPath)
df.to_csv(destinationPath, index=False)