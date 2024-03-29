from flask import Flask, render_template, request, redirect
import requests
import json


# get_sorted_recommendations(["Bridesmaids", "Sherlock Holmes"])
def get_movies_from_tastedive(name):
    parameters = {"q": name, "type": "movies", "limit": 5, 'k':'365607-Omkar-SQO9AI0G'}
    tastedive_response = requests.get("https://tastedive.com/api/similar", params=parameters)
    py_data = json.loads(tastedive_response.text)
    return py_data


def extract_movie_titles(dic_from_get_movies):
    movie_title = list()
    movie_info = dic_from_get_movies["Similar"]["Results"]
    for movie in movie_info:
        movie_title.append(movie["Name"])
    return movie_title


def get_related_titles(list_of_movie_title):
    new_list = list()
    for title in list_of_movie_title:
        a = get_movies_from_tastedive(title)
        b = extract_movie_titles(a)
        for movie in b:
            if movie not in new_list:
                new_list.append(movie)
    return new_list


def get_movie_data(movie_name):
    parameters = {'t': movie_name, 'r': 'json','apikey':'2b8254a2'}
    omdbapi_response = requests.get('http://www.omdbapi.com/', params=parameters)
    a = json.loads(omdbapi_response.text)
    return a


def get_movie_rating(movie_dict):
    if len(movie_dict['Ratings']) > 1:
        if movie_dict['Ratings'][1]['Source'] == 'Rotten Tomatoes':
            if(len(movie_dict['Ratings'][1]['Value'])<3):
                rotten_rating = movie_dict['Ratings'][1]['Value'][:1]
                rotten_rating = int(rotten_rating)
            else:
                rotten_rating = movie_dict['Ratings'][1]['Value'][:2]
                rotten_rating = int(rotten_rating)
    else:
        rotten_rating = 0

    return rotten_rating


def getkey(item):
    return item[1]


def get_sorted_recommendations(list_of_movies):
    related_movies = get_related_titles(list_of_movies)
    ratings = list()
    sorted_list = list()
    for movie in related_movies:
        a = get_movie_data(movie)
        ratings.append(get_movie_rating(a))

    temp_tuple1 = zip(related_movies, ratings)
    temp_tuple2 = sorted(temp_tuple1, key=getkey, reverse=True)
    for i in range(len(temp_tuple2) - 1):
        if temp_tuple2[i][0] not in sorted_list:
            if temp_tuple2[i][1] == temp_tuple2[i + 1][1]:
                if temp_tuple2[i][0] < temp_tuple2[i + 1][0]:
                    sorted_list.append(temp_tuple2[i + 1][0])
                    sorted_list.append(temp_tuple2[i][0])
            else:
                sorted_list.append(temp_tuple2[i][0])

    return sorted_list

def block(name):
    finalList = get_sorted_recommendations([name])
    return finalList

app=Flask(__name__)

@app.route('/', methods=['Get', 'Post'])
def homePage():
    
    if request.method == 'POST':
        name = request.form['title']
        url = '/' + name
        return redirect(url) 
    else:
        return render_template('movie.html')

@app.route('/<string:name>', methods=['Get', 'Post'])
def recommendation(name):
    if request.method == 'POST':
        name = request.form['title']
        url = '/' + name
        return redirect(url)
    else:
        lis1 = block(name)
        return render_template('recommendation2.html', lis=lis1)



if __name__=='__main__': #this runs if application run form terminal in debug mode  
    app.run(debug=True)