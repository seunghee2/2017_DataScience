#-*- coding: utf-8 -*-

import sys
import os
import glob
import json
from pandas.io.json import json_normalize

# py 파일이 존재하는 directory 내 'A000' paths 반환
def get_paths():
    paths = []
    for i in range(1, 99):
        paths.append(sys.path[0] + "/sokulee/A0" + str(i))
    return paths

"""
 1부터 98까지 모든 user가 존재하진 않기 때문에
 향후 폴더 내 존재하는 number의 user만 체크하기 위해 array 선언
"""
user_name_indices = []

# 각 json 파일들의 내용을 array로 추출
def get_merges_json(flist):
    temp = []
    for f in flist:
        i = 0
        for str in f.split("/"):
            if "A0" not in str:
                i += 1
            else:
                break
        if f.split("/")[i] not in user_name_indices:
            user_name_indices.append(f.split("/")[i])
        with open(f) as result:
            data = json.load(result)
            temp.append(data)
    return temp

# title이 포함된 모든 파일들의 내용을 하나의 json 데이터로 merge
def merging_users_data(paths, title):
    datas = []
    for path in paths:
        file_mask = os.path.join(path, '*%s.json' % title)
        temp = []
        for values in get_merges_json(glob.glob(file_mask)):
            temp.append(values)
        datas.append(temp)

    return datas

"""
 각 user의 sleep data를 추출

 sleep: 기록된 수면 로그들의 집합 (없을수도, 한 개일수도, 여러개일수도)
 dateOfSleep: 수면 로그가 기록된 날짜
 minutesAsleep: 실제 수면을 취한 시간(분)
 minutesAwake: 수면 중 awake한 시간(분)
 totalMinutesAsleep: 총 수면을 취한 시간(분)
"""
def get_each_sleeps_data_in_users(users_data):
    users = {}
    index = 0
    for user in users_data:
        users_data = {}
        for single_date in user:
            if 'summary' in single_date and 'sleep' in single_date:
                summary_result = json_normalize(single_date['summary'])
                if len(single_date['sleep']) > 1:
                    sleep_logs = json_normalize(single_date['sleep'][0])
                elif len(single_date['sleep']) == 1:
                    sleep_logs = json_normalize(single_date['sleep'])
                date = sleep_logs['dateOfSleep'].iloc[0]
                users_data[date] = \
                    {'minutesAsleep': int(summary_result['totalMinutesAsleep']),
                    'minutesAwake':int(summary_result['totalTimeInBed']) - int(summary_result['totalMinutesAsleep'])}
        if len(users_data) > 0:
            users[user_name_indices[index]] = users_data
            index += 1
    return users



"""""""""""""""""""""""
 ******* main *******
"""""""""""""""""""""""
users_data = merging_users_data(get_paths(), 'sleep')
users_sleeps = get_each_sleeps_data_in_users(users_data)

"""
 사용자마다 기록되지 않은 date가 존재하기 때문에
 데이터가 기록된 모든 date를 추출하기 위해 logged_dates를 정의한다
"""
logged_dates = []
for user in users_sleeps:
    for key in users_sleeps[user]:
        if key not in logged_dates:
            logged_dates.append(key)

# 사용자의 time_for_awake 데이터와 time_for_sleep 데이터 정의
time_for_awake = []
time_for_sleep = []
for date in logged_dates:
    total_awake = 0
    total_sleep = 0
    for user in users_sleeps:
        if date in users_sleeps[user].keys():
            total_sleep += users_sleeps[user][date]['minutesAsleep']
            total_awake += users_sleeps[user][date]['minutesAwake']
        else:
            total_sleep += 0
            total_awake += 0
    time_for_awake.append(total_awake / len(users_sleeps))
    time_for_sleep.append(total_sleep / len(users_sleeps))

# 총 수면 데이터를 요일별로 재정의
import pandas as pd

sleep_for_weeks = []
weeks = pd.DatetimeIndex(logged_dates).weekday.tolist()

for i in range(0, 7):
    total = 0
    for value in weeks:
        if value == i:
            total += (time_for_awake[weeks.index(value)] + time_for_sleep[weeks.index(value)])
    sleep_for_weeks.append(total)

# draw the two graphs
import matplotlib.pyplot as plt
import numpy as np
import datetime

fig = plt.figure(1)
width = 0.8

# logged date는 날짜순이 아닌 배열이므로 이를 날짜순으로 재정렬 (실질적인 데이터는 날짜순으로 기록되어있을 것)
x_axis = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in logged_dates]
x_axis.sort()
x_axis = [datetime.datetime.strftime(date, "%Y-%m-%d") for date in x_axis]

# the first graph
graph = fig.add_subplot(211)
awake = graph.plot(range(len(x_axis)), time_for_awake, color='#68b37d', label="Time for awake")
sleep = graph.plot(range(len(x_axis)), time_for_sleep, color='#5f88bc', label="Time for sleep")
graph.set_xticks(np.arange(len(x_axis)))
graph.set_xticklabels(x_axis, rotation=90, fontsize=7)
graph.legend(loc='best', shadow=True, fancybox=True, numpoints=1)
plt.ylabel('Minutes')
plt.title('The Relationship Between The Sleep Time(Each Awakes and Sleeps) and The Dates')

# the second graph
graph = fig.add_subplot(212)
week_name = ['Mon', 'Tue', 'Wed', 'Tur', 'Fri', 'Sat', 'Sun']
graph.bar(range(0, 7), sleep_for_weeks, width=width, color='#cf6567', align='center')
graph.set_xticks(np.arange(len(week_name)))
graph.set_xticklabels(week_name)
plt.ylabel('Minutes')
plt.title('Average Sleep Time Per Day')

plt.show()

