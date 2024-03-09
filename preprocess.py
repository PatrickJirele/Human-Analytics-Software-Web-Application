from appConfig import *

# TO DO:
# Combine Race & Ethnicity


# UNABBREVIATION DICTIONARIES
# Note: If a key:value pair has a value of 1, the key will be used as the unabbreviation.


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
    #df.rename(columns={'Hire Date' : 'Years At Western'}, inplace=True) #For when we use official dataset

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

def modifyName(column_name):
    if "/" in column_name:
        return column_name.replace("/", "-")
    else:
        return column_name

