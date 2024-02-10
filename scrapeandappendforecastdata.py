# -*- coding: utf-8 -*-
"""ScrapeandAppendForecastData.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Rz0MA1Ooa6x8OlgE6Q2S6YI1eJCKuiSz
"""

import pandas as pd
import matplotlib.pyplot as plt
import keras
import requests
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
import csv

"""
Since the time doesn't return a date and the data is pulled in reverse chronological order
"""


def main():
    today = date.today() - timedelta(days=1)

    path = ''

    url = "https://www.localconditions.com/weather-alhambra-california/91801/past.php"
    file = requests.get(url).content
    soup = BeautifulSoup(file, "html.parser")

    headers = ['Time PST', 'Temp (F)', 'Humidity', "Dew Point", 'Barometer', 'Wind Speed (in HG)', 'Wind Direction',
               'Wind Gust (MPH)', '1hr. Precip / Rain Total (in.)', 'Snow Depth']

    dictionary_data = {}
    for key in headers:
        dictionary_data[key] = []

    """
    all the data regarding the temperature have a table header
    
    each hour stamp is separated by a tr
    
    each column is separated by a td
    """

    for i in range(1, len(soup.findAll('table'))):
        temp = soup.findAll('table')[i].findAll('tr')
        for j in range(1, len(temp) - 1):
            parse = temp[j].find_all("td")
            if len(parse) != 10:
                continue
            for index, (key) in enumerate(dictionary_data.keys()):
                if key == 'Time PST':
                    dictionary_data[key].append("{} {}".format(today - timedelta(days=i), parse[index].text))
                else:
                    dictionary_data[key].append(parse[index].text)

    pd_data = pd.DataFrame.from_dict(dictionary_data)
    pd_data = pd_data.drop(['Dew Point', 'Barometer', '1hr. Precip / Rain Total (in.)', 'Snow Depth', 'Wind Direction'],
                           axis=1)

    new_headers = ['Time PST', 'Temp (F)', 'Humidity', 'Wind Speed (in HG)', 'Wind Gust (MPH)']

    for header in new_headers:
        pd_data = pd_data[pd_data[header] != '-']

    pd_data['Time PST'] = pd.to_datetime(pd_data['Time PST'])
    pd_data = pd_data.iloc[::-1]
    pd_data.reset_index(drop=True, inplace=True)
    pd_data['Temp (F)'] = pd_data['Temp (F)'].astype(int)
    pd_data['Humidity'] = pd_data['Humidity'].astype(int)
    pd_data['Wind Speed (in HG)'] = pd_data['Wind Speed (in HG)'].astype(float)
    pd_data['Wind Gust (MPH)'] = pd_data['Wind Gust (MPH)'].astype(float)

    pd_data.to_csv(path + 'weather_data.csv', mode='a', index=False, header=False)

    remove_dup = pd.read_csv(path + 'weather_data.csv')

    remove_dup = remove_dup.drop_duplicates(subset=['Time PST'])

    remove_dup.to_csv(path + 'weather_data.csv', mode='w', index=False, header=True)


if __name__ == 'main':
    main()
