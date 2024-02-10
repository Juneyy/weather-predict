# -*- coding: utf-8 -*-
"""Load Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CnM4IpjNR-VDFbqUuaVm96Q0cMkzkeAu
"""

import pandas as pd
import keras
import tensorflow as tf
import requests
import numpy as np
import csv

from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup

# path = '/content/drive/MyDrive/WeatherForecast/'
path = ''


def preprocessdata():
"""To get the training data mean and std for the features"""
    with open(path + 'Preprocessing_Data.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    version = int(*data[0])
    mean = data[2]
    std = data[3]

    for i in range(len(mean)):
        mean[i] = float(mean[i])
        std[i] = float(std[i])
    return version, mean, std


def normalize(data):
    data['Temp (F)'] = (data['Temp (F)'] - mean[0]) / std[0]
    data['Humidity'] = (data['Humidity'] - mean[1]) / std[1]
    data['Dew Point'] = (data['Dew Point'] - mean[2]) / std[2]
    data['Wind Speed (in HG)'] = (data['Wind Speed (in HG)'] - mean[3]) / std[3]
    data['Wind Gust (MPH)'] = (data['Wind Gust (MPH)'] - mean[4]) / std[4]
    return data


def getdata(mean, std):
    url = "https://www.localconditions.com/weather-alhambra-california/91801/past.php"
    file = requests.get(url).content

    soup = BeautifulSoup(file, "html.parser")

    headers = ['Time PST', 'Temp (F)', 'Humidity', "Dew Point", 'Barometer', 'Wind Speed (in HG)', 'Wind Direction',
               'Wind Gust (MPH)', '1hr. Precip / Rain Total (in.)', 'Snow Depth']

    dictionary_data = {}
    for key in headers:
        dictionary_data[key] = []

    for i in range(0, len(soup.findAll('table'))):
        temp = soup.findAll('table')[i].findAll('tr')
        for j in range(1, len(temp) - 1):
            parse = temp[j].find_all("td")
            if len(parse) != 10:
                continue
            for index, (key) in enumerate(dictionary_data.keys()):
                dictionary_data[key].append(parse[index].text)

    pd_data = pd.DataFrame.from_dict(dictionary_data)
    pd_data = pd_data.drop(['Time PST', 'Barometer', '1hr. Precip / Rain Total (in.)', 'Snow Depth', 'Wind Direction'],
                           axis=1)

    new_headers = ['Temp (F)', 'Humidity', "Dew Point", 'Wind Speed (in HG)', 'Wind Gust (MPH)']

    for header in new_headers:
        pd_data = pd_data[pd_data[header] != '-']

    pd_data = pd_data.iloc[::-1]
    pd_data.reset_index(drop=True, inplace=True)
    pd_data['Temp (F)'] = pd_data['Temp (F)'].astype(int)
    pd_data['Humidity'] = pd_data['Humidity'].astype(int)
    pd_data['Dew Point'] = pd_data['Dew Point'].astype(float)
    pd_data['Wind Speed (in HG)'] = pd_data['Wind Speed (in HG)'].astype(float)
    pd_data['Wind Gust (MPH)'] = pd_data['Wind Gust (MPH)'].astype(float)

    pd_data = pd_data.iloc[0:60]
    df = normalize(pd_data)
    tf_data = tf.convert_to_tensor(df)
    tf_data = tf.reshape(tf_data, [1, *tf_data.shape])
    return tf_data


def main():
    version, mean, std = preprocessdata()
    data = getdata(mean, std)

    model = tf.keras.models.load_model(path + 'LTSM{}.keras'.format(version))

    prediction = model.predict(tf_data)

    with open('output.txt', 'a') as f:
        f.write("Prediction {}\n".format(prediction[0][0] * std[0] + mean[0]))


if __name__ == "__main__":
    main()
