from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired,NumberRange,URL
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap5(app)

# CREATE DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top_10.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# CREATE TABLE
class Movie(db.Model):
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    title:Mapped[str] = mapped_column(String(250),unique=True,nullable=False)
    year: Mapped[int] = mapped_column(Integer,nullable=False)
    description:Mapped[str] = mapped_column(String(1000),nullable=False)
    rating:Mapped[float] = mapped_column(Float,nullable=False)
    ranking:Mapped[int] = mapped_column(Integer,nullable=False)
    review : Mapped[int] = mapped_column(String(250),nullable=False)
    img_url : Mapped[str] = mapped_column(String(500),nullable=False)

#----------------------------------------Home Page----------------------------------------#
@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.ranking))
    movies = reversed(result.scalars().all())
    return render_template("index.html",movies = movies)

#------------------------------------Adding a movie--------------------------------------#

class AddMovie(FlaskForm):
    title = StringField("What's the name of the movies? ",validators=[DataRequired()])
    year = IntegerField("What year it was released in?",validators=[DataRequired()])
    description = StringField("Write a little description of the movie : ",validators=[DataRequired()])
    rating = FloatField("Enter the rating : ",validators=[DataRequired(),NumberRange(0,10)])
    ranking = IntegerField("Enter the your ranking : ",validators=[DataRequired(),NumberRange(min = 0,max=10)])
    review = StringField("Enter your review : ",validators=[DataRequired()])
    img_url = StringField("Enter the image url : ",validators=[DataRequired(),URL()])
    submit = SubmitField("Add Movie")

@app.route("/add",methods=["POST","GET"])
def add_movie():
    form = AddMovie()
    if form.validate_on_submit():
        movie = Movie(title = form.title.data,year = int(form.year.data), description = form.description.data,rating = float(form.rating.data),ranking = int(form.ranking.data),review = form.review.data,img_url = form.img_url.data)
        db.session.add(movie)
        db.session.commit()
        return redirect("/")
    return render_template("add.html",form = form)

#--------------Delete the movie----------------#
@app.route("/delete?id=<int:movie_id>")
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect("/")
#------------Update the movie-----------#
@app.route("/update?id=<int:movie_id>",methods=["GET","POST"])
def update_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = AddMovie()
    if request.method == 'GET':
        form.title.data = movie.title
        form.year.data = movie.year
        form.description.data  =  movie.description
        form.rating.data = movie.rating
        form.ranking.data = movie.ranking
        form.review.data = movie.review
        form.img_url.data = movie.img_url
        form.submit.label.text = "Update"
    if form.validate_on_submit():
       movie.title =  form.title.data
       movie.year =  form.year.data
       movie.description = form.description.data
       movie.rating = form.rating.data
       movie.ranking = form.ranking.data
       movie.review = form.review.data
       movie.img_url = form.img_url.data
       db.session.commit()
       return  redirect("/")
    return render_template("edit.html",form=form,movie_id=movie_id)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
