from config import key
import pandas as pd
"""
Converts csv into a list of daily deaths/new cases 
"""
def date_to_int(date):
    """
    :param date: date in format YYYY-MM-DD
    :return: int, days from 2020-01-21
    """
    month_len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if date[0:4] != "2020":
        raise RuntimeError('Year Invalid')
        return None

    month = int(date[5:7]) - 1 # month jan = 0, dec = 11
    day = int(date[8:])
    return sum(month_len[0:month]) + day - 21 # sum the len of months before + day into current month - 21 to account
    # for starting on the 21 of jan
def csv_to_data(file):
    df = pd.read_csv(file)
    data = [{}] * (date_to_int(df['date'][len(df['date'])-1]) + 1) # making a list, len = days since 2020-01-21, +1 nc count starts at 0
    # data in constructed in format as a list of [total cases, total deaths, daily cases, daily deaths], by fip
    prev_date = df['date'][0] # setting prev_date to the start date
    index_data = 0 # setting index which corresponds to data to 0
    uncounted = 0 # number of uncounted deaths due to lack of fips code
    for i in range(len(df['date'])):
        date = df['date'][i]
        try:
            county_key = df['state'][i] +"," + df['county'][i]
        except ValueError:
            uncounted += 1
            continue
        if prev_date != date:
            prev_date = date
            index_data = date_to_int(date)
        try:
            prev_cases = data[index_data - 1][county_key][0]
            prev_deaths = data[index_data - 1][county_key][1]
        except KeyError:
            prev_cases, prev_deaths = 0, 0
        if len(data[index_data]) == 0:
            data[index_data] = {county_key: [df['cases'][i], df['deaths'][i], df['cases'][i] - prev_cases, df['deaths'][i] - prev_deaths]}
        else:
            data[index_data].update({county_key: [df['cases'][i], df['deaths'][i], df['cases'][i] - prev_cases, df['deaths'][i] - prev_deaths]})
    return data

