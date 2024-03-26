from appConfig import *

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
def modifyName(df, columnName):
    newName = columnName
    if "/" in newName:
        newName = newName.replace("/", "_")
    df.rename(columns={columnName:newName}, inplace=True)
    return df

