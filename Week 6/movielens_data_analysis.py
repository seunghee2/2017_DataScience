import pandas as pd

def movie_lens_data_load():
    ratings = pd.read_csv("/Users/leeseunghee/Desktop/data science/ml-20m/ratings.csv")
    return ratings

ratings = movie_lens_data_load()

um_matrix_ds = ratings.pivot(index='userId', columns='movieId', values='rating')

# extract the 20 users for test
user_loc = [p * 1000 for p in range(1, 21)]
users_for_test = ratings.loc[user_loc]
print(users_for_test)

import math
from scipy.spatial import distance

def distance_cosine(a, b):
    return 1 - distance.cosine(a, b)

def distance_correlation(a, b):
    return 1 - distance.correlation(a, b)

def distance_euclidean(a, b):
    return 1 / (distance.euclidean(a, b) + 1)

from operator import itemgetter

def nearest_neighbor_user(user, top_n, similarity_func):
    base_user = um_matrix_ds.loc[user].dropna()
    rated_index = base_user.index
    nearest_neighbor = {}
    
    for user_id, row_data in um_matrix_ds.iterrows():
        intersection_user1 = []
        intersection_user2 = []
        if user == user_id:
            continue
        
        for index in rated_index:
            if math.isnan(row_data[index]) == False:
                intersection_user1.append(base_user[index])
                intersection_user2.append(row_data[index])
    
        if len(intersection_user1) < 3:
            continue

        similarity = similarity_func(intersection_user1, intersection_user2)
    
        if math.isnan(similarity) == False:
            nearest_neighbor[user_id] = similarity
    
    return sorted(nearest_neighbor.items(), key=itemgetter(1))[:-(top_n + 1):-1]

st = time.time()
for id in users_for_test.userId:
    print('the nearest 3 of user ', id, ' : ', nearest_neighbor_user(id, 3, distance_euclidean))
print('in ', time.time() - st, ' sec')

def predict_ration(user_id, movie_id, nearest_neighbor = 10000, similarity_func = distance_euclidean):
    neighbor = nearest_neighbor_user(user_id, nearest_neighbor, similarity_func)
    neighbor_id = [id for id, sim in neighbor]
    
    neighbor_movie = um_matrix_ds.loc[neighbor_id].dropna(1, how='all', thresh=4)
    neighbor_dic = (dict(neighbor))
    for movieId, row in neighbor_movie.iteritems():
        if movie_id == movieId:
            jsum, wsum = 0, 0
            for v in row.dropna().iteritems():
                sim = neighbor_dic.get(v[0], 0)
                jsum += sim
                wsum += (v[1] * sim)
            return wsum / jsum

print('predict the ration of each 20 users')

'''
for i in users_for_test.index:
    user_id = users_for_test['userId'][i]
    movie_id = users_for_test['movieId'][i]
    rating = users_for_test['rating'][i]
    print('user ', user_id, 'in movie Id ', movie_id, ' original ration ', rating, 'predicted ration ', predict_ration(user_id, movie_id))
'''

predicted = []
for i in users_for_test.index:
    user_id = users_for_test['userId'][i]
    movie_id = users_for_test['movieId'][i]
    rating = users_for_test['rating'][i]
    predicted_ration = predict_ration(user_id, movie_id)
    predicted.append([user_id, predicted_ration])
    print('user ', user_id, 'in movie Id ', movie_id, ' original ration ', rating, 'predicted ration ', predicted_ration)


import numpy as np

def RMSE(X, left_col, right_col):
    return(np.sqrt(np.mean((X[left_col] - X[right_col])**2)))

def MAE(X, left_col, right_col):
    return(np.mean(np.absolute(X[left_col] - X[right_col])))

df = pd.DataFrame(users_for_test)
euclidean = []

for row in predicted:
    euclidean.append(row[1])

df['euclidean'] = pd.Series(euclidean).values

print('mean absolute error : ', MAE(df, 'rating', 'euclidean'))
print('root mean square error : ', RMSE(df, 'rating', 'euclidean'))
