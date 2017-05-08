import fitbit
from datetime import timedelta, date
import json
import io
import os

# a method for get the data according to each dates
def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

# get fitbit data and create a json file
def createFile():
    authd_client = fitbit.Fitbit('228D6B', 'eec0b22c7dc9a02ba35f3711ccf6e29a', access_token='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0UVQzRlAiLCJhdWQiOiIyMjhENkIiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd251dCB3cHJvIHdzbGUgd3dlaSB3c29jIHdhY3Qgd3NldCB3bG9jIiwiZXhwIjoxNDkwNzkzODkyLCJpYXQiOjE0OTA3NjUwOTJ9.zz58ZiJomcG-70dAPVYQs6VLaDDRG13Vld6db0ArLyk', refresh_token='0221bdcc33585018dc20a1d152dd439f388d116db4876ff857cc3f513d0c8b0b')
    start_date = date(2017, 3, 15)
    end_date = date(2017, 3, 29)

    intraday_steps= []
    for single_date in daterange(start_date, end_date):
        print(single_date)
        intraday_steps.append(authd_client.intraday_time_series('activities/steps', base_date=single_date.strftime("%Y-%m-%d"), detail_level='15min'))
    with open('Result.json', 'w') as outfile:
        json.dump(intraday_steps, outfile)

# get data from the json file
def getDataFromFile():
    with open('Result.json') as result_json:
        data = json.load(result_json)
        from pandas.io.json import json_normalize
        result = json_normalize(data, 'activities-steps')
    return result

# file checking
def isExistReadableFile():
    if os.path.exists('Result.json'):
        print("File exists and is readable")
    else:
        print("Either file is missing or is not readable, creating file...")
        createFile()

# main
isExistReadableFile()
result = getDataFromFile()


##---- drawing the graph ----##

x_axis = []
y_axis = []

import datetime

for date in result['dateTime']:
    x_axis.append(datetime.datetime.strptime(date, "%Y-%m-%d").date())

# save maximum value of the steps
maximum = 0
for value in result['value']:
    if int(value) > maximum:
        maximum = int(value)
    y_axis.append(int(value))


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
graph = fig.add_subplot(111)
width = 0.8

# custom color
colors = [((15 % (x + 1))/10.0, (14 % (x + 1))/20.0, 0.75) for x in range(len(x_axis))]
graph.bar(range(len(x_axis)), y_axis, width=width, color=colors)

graph.set_xticks(np.arange(len(x_axis)) + width / 2)
graph.set_xticklabels(x_axis, rotation=45)

# draw a label of the maximum value
rects = graph.patches
labels_max = ["Max : %d" % i for i in y_axis]
for rect, label in zip(rects, labels_max):
    if y_axis.index(maximum) == labels_max.index(label):
        height = rect.get_height()
        graph.text(rect.get_x() + rect.get_width() / 2, height + 8, label, ha='center', va='bottom', color='r')

plt.xlabel('Date')
plt.ylabel('Steps')
plt.title('Seunghee\'s Steps Data')
plt.show()
