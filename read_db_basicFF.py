""" read from a SQLite database and return data """

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

Bootstrap(app)

# the name of the database; add path if necessary
db_name = 'filmflix.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

# each table in the database needs a class to be created for it
# db.Model is required - don't change it
# identify all columns by name and data type


class Film(db.Model):
    __tablename__ = 'tblFilms'
    filmID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    yearReleased = db.Column(db.Integer)
    rating = db.Column(db.String)
    duration = db.Column(db.Integer)
    genre = db.Column(db.String)

# routes


@app.route('/')
def index():
    try:
        films = Film.query.filter_by(genre='Action').order_by(Film.title).all()
        film_text = '<ul>'
        for film in films:
            film_text += '<li>' + film.title + ', ' + film.rating + '</li>'
        film_text += '</ul>'
        return film_text
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/inventory/<genre>')
def inventory(genre):
    films = Film.query.filter_by(genre=genre).order_by(Film.title).all()
    return render_template('listFF.html', films=films, genre=genre)


if __name__ == '__main__':
    app.run(debug=True)
