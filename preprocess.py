from appConfig import *

# TO DO:
# Combine Race & Ethnicity


# UNABBREVIATION DICTIONARIES
# NOTE: If a key:value pair has a value of 1, the key will be used as the unabbreviation.


# PRECONDITION: A dataframe is provided containing a column named "Years At Western" with values formated at "%m/%d/%Y"
# POSTCONDITION: The dataframe is returned with every value in the "Years At Western" column reformatted as the number of years since the current date, rounded down.
def reformatYearsColumn(df):
    columnName = 'Years At Western'
    df.rename(columns={'Hire Date':columnName}, inplace=True)

    for i in range(len(df)):
        value = df.loc[i, columnName]
        try:
            rd = relativedelta.relativedelta(datetime.now(), value)
            df.loc[i,columnName] = rd.years
        except Exception as e:
            print(e)
            df.loc[i,columnName] = ''
    return df

# PRECONDITION: A dataframe is provided with the columns "Race/Ethnicity", "Gender", and "Employee Type".
# POSTCONDITION: The dataframe is returned with all info unabreviated and invalid values removed. Entire rows with multiple invalid values are potentially removed
#                depending on maxNumberOfMissingCells value.
# NOTE: NOT IN USE
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


# PRECONDITION:
# POSTCONDITION: 
def combineRaceAndEthnicity(df):
    for i in range(len(df)):
        race = df.loc[i, 'Race/Ethnicity']
        isHispanicLatino = (df.loc[i, 'Hispanic or Latino'] == 'Yes')
        if (race == 'White (United States of America)' and isHispanicLatino):
            df.loc[i,'Race/Ethnicity'] = 'Histpanic or Latino'
        elif (isHispanicLatino):
            df.loc[i,'Race/Ethnicity'] = 'Two or More Races (United States of America)'
    return df

# PRECONDITION:
# POSTCONDITION: 
def modifyName(column_name):
    if "/" in column_name:
        return column_name.replace("/", "-")
    else:
        return column_name

