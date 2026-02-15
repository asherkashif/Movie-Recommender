import pickle
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ===== Load Data =====
movies = pickle.load(open("movie_list .pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

movies['title_lower'] = movies['title'].str.lower()


# ===== Fetch Poster =====
def fetch_poster(movie_id):
    api_key = "8265bd1679663a7ea12ac168da84d2e8"

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        data = requests.get(url).json()

        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except:
        return "https://via.placeholder.com/500x750?text=Error"


# ===== Recommendation Logic =====
def recommend(movie):
    movie = movie.lower()

    if movie not in movies['title_lower'].values:
        return [], []

    movie_index = movies[movies['title_lower'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# ===== Main Page =====
@app.route("/")
def home():
    return render_template("index.html", movies_list=movies['title'].values)


# ===== AJAX API =====
@app.route("/recommend", methods=["POST"])
def get_recommendations():
    movie_name = request.json["movie"]

    names, posters = recommend(movie_name)

    return jsonify({
        "names": names,
        "posters": posters
    })


if __name__ == "__main__":
    app.run(debug=True)
