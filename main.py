from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, sessionmaker
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, UpdateForm, RegisterForm, AddMovieForm
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///top_movies.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Configuring for user login and logout
login_manager = LoginManager()
login_manager.init_app(app)


# Managing the logged-in user session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # This will act like a List of movies objects attached to each User.
    # The "user" refers to the author property in the BlogPost class.
    movies = relationship("Movie", back_populates="user")  # relationship with Movie table


class Movie(db.Model):
    __tablename__ = "fav_movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    # Create Foreign Key, "users.id" the users refers to the table name of User.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # defining foreign key
    user = relationship("User", back_populates="movies")  # relationship with users table


with app.app_context():
    db.create_all()





@app.route("/")
def home():
    # Authenticate user to show blogs otherwise redirect to login page
    if current_user.is_authenticated:
        movies = Movie.query.filter_by(user_id=current_user.id).all()
        for i in range(len(movies)):
            movies[i].ranking = len(movies) - i
        db.session.commit()
    else:
        return redirect(url_for('login'))

    return render_template("index.html", movies=movies)


@app.route("/register", methods=["GET", "POST"])
def register():
    # New user registration
    new_user = User()  # User database class instance

    register_form = RegisterForm()

    if request.method == "POST":

        # Registering new user
        if register_form.validate_on_submit():

            # User already exists
            if User.query.filter_by(username=register_form.username.data).first():
                flash("You've already signed up with that email, log in instead!")
                return redirect(url_for('login'))

            # new user
            else:
                new_user.name = register_form.name.data
                new_user.username = register_form.username.data
                # hashing and salting the user password
                hashed_password = generate_password_hash(password=register_form.password.data, salt_length=8)
                new_user.password = hashed_password

                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('home'))

    return render_template("register.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Registration of new user
    login_form = LoginForm()

    if request.method == "POST":
        username = None
        password = None

        if login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("This email does not exist, please try again ")
            return redirect(url_for('login'))

        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))

        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/find")
@login_required
def find():
    movie_id = request.args.get('id')
    IMAGE_TMDB_URL = "https://image.tmdb.org/t/p/w500/"

    if movie_id:
        tmdb_id_endpoint = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": "4bd1624a27cd5d13784e874c693281be"}

        response = requests.get(url=tmdb_id_endpoint, params=params)
        data = response.json()

        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{IMAGE_TMDB_URL}{data['poster_path']}",
            description=data["overview"],
            rating=7.5,
            ranking=10,
            review="Great",
            user_id = current_user.id
        )
        db.session.add(new_movie)
        db.session.commit()

    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # Adds new movie in the database and display
    add_movie_form = AddMovieForm()
    if add_movie_form.validate_on_submit():
        movie_title = add_movie_form.title.data
        tmdb_endpoint = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": "4bd1624a27cd5d13784e874c693281be",
                  "query": movie_title}

        response = requests.get(url=tmdb_endpoint, params=params)
        data = response.json()['results']

        return render_template('select.html', options=data)

    return render_template("add.html", form=add_movie_form)


@app.route("/delete")
@login_required
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    form = UpdateForm()
    if form.validate_on_submit():
        movie_id = request.args.get('id')
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
