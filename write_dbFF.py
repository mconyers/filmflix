""" write to a SQLite database with forms, templates
    add new record, delete a record, edit/update a record
    """

from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from datetime import date

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# Flask-Bootstrap requires this line
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

    def __init__(self, title, yearReleased, rating, duration, genre):
        self.title = title
        self.yearReleased = yearReleased
        self.rating = rating
        self.duration = duration
        self.genre = genre

# +++++++++++++++++++++++
# forms with Flask-WTF

# form for add_record and edit_or_delete
# each field includes validation requirements and messages


class AddRecord(FlaskForm):
    # id used only by update/edit
    id_field = HiddenField()
    title = StringField('Film title', [InputRequired(),
                                       Regexp(r'^[A-Za-z\s\-\']+$',
                                              message="Invalid film name"),
                                       Length(min=1, max=150,
                                              message="Invalid film name length")
                                       ])
    yearReleased = IntegerField('Year film was released', [InputRequired(),
                                                           NumberRange(
        min=1900, max=2023, message="Invalid range")
    ])
    rating = SelectField('Choose the fim rating', [InputRequired()],
                         choices=[('', ''), ('G', 'G'),
                                  ('U', 'U'),
                                  ('PG', 'PG'),
                                  ('12A', '12A'),
                                  ('15', '15'),
                                  ('18', '18'),
                                  ('R', 'R')])
    duration = IntegerField('Length of films (mins))', [InputRequired(),
                                                        NumberRange(
        min=1, max=1265, message="Invalid range")
    ])
    genre = SelectField('Choose the fim genre', [InputRequired()],
                        choices=[('', ''), ('Action', 'Action'),
                                 ('Animation', 'Animation'),
                                 ('Comedy', 'Comedy'),
                                 ('Crime', 'Crime'),
                                 ('Drama', 'Drama'),
                                 ('Fantasy', 'Fantasy'),
                                 ('Fighting', 'Fighting'),
                                 ('Musical', 'Musical'),
                                 ('Period', 'Period'),
                                 ('Rom-Com', 'Rom-Com'),
                                 ('Sci-Fi', 'Sci-Fi'),
                                 ('Thriller', 'Thriller'),
                                 ('War', 'War')])

    # updated - date - handled in the route
    updated = HiddenField()
    submit = SubmitField('Add/Update Record')

# small form


class DeleteForm(FlaskForm):
    id_field = HiddenField()
    purpose = HiddenField()
    submit = SubmitField('Delete This Film')

# +++++++++++++++++++++++
# get local date - does not account for time zone
# note: date was imported at top of script


def stringdate():
    today = date.today()
    date_list = str(today).split('-')
    # build string in format 01-01-2000
    date_string = date_list[1] + "-" + date_list[2] + "-" + date_list[0]
    return date_string

# +++++++++++++++++++++++
# routes


@app.route('/')
def index():
    # get a list of unique values in the genre column
    genres = Film.query.with_entities(Film.genre).distinct()
    return render_template('index.html', genres=genres)


@app.route('/inventory/<genre>')
def inventory(genre):
    films = Film.query.filter_by(genre=genre).order_by(Film.title).all()
    return render_template('listFF.html', films=films, genre=genre)

# add a new film to the database


@app.route('/add_recordFF', methods=['GET', 'POST'])
def add_record():
    form1 = AddRecord()
    if form1.validate_on_submit():
        title = request.form['title']
        yearReleased = request.form['yearReleased']
        rating = request.form['rating']
        duration = request.form['duration']
        genre = request.form['genre']
        # get today's date from function, above all the routes
        # updated = stringdate()
        # the data to be inserted into Sock model - the table, socks
        record = Film(title, yearReleased, rating, duration, genre)
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        # create a message to send to the template
        message = f"The data for the film, {title} has been submitted."
        return render_template('add_recordFF.html', message=message)
    else:
        # show validaton errors
        # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('add_recordFF.html', form1=form1)

# select a record to edit or delete


@app.route('/select_record/<letters>')
def select_record(letters):
    # alphabetical lists by film name, chunked by letters between _ and _
    # .between() evaluates first letter of a string
    a, b = list(letters)
    films = Film.query.filter(Film.title.between(a, b)
                              ).order_by(Film.title).all()
    return render_template('select_record.html', films=films)

# edit or delete - come here from form in /select_record


@app.route('/edit_or_delete', methods=['POST'])
def edit_or_delete():
    id = request.form['id']
    print(f'Film id is {id}')
    choice = request.form['choice']
    film = Film.query.filter(Film.filmID == id).first()
    # two forms in this template
    form1 = AddRecord()
    form2 = DeleteForm()
    return render_template('edit_or_delete.html', film=film, form1=form1, form2=form2, choice=choice)

# result of delete - this function deletes the record


@app.route('/delete_result', methods=['POST'])
def delete_result():
    id = request.form['id_field']
    purpose = request.form['purpose']
    film = Film.query.filter(Film.filmID == id).first()
    if purpose == 'delete':
        db.session.delete(film)
        db.session.commit()
        message = f"The film {film.title} has been deleted from the database."
        return render_template('resultFF.html', message=message)
    else:
        # this calls an error handler
        abort(405)

# result of edit - this function updates the record


@app.route('/edit_result', methods=['POST'])
def edit_result():
    id = request.form['id_field']
    # call up the record from the database
    film = Film.query.filter(Film.filmID == id).first()
    # update all values
    film.title = request.form['title']
    film.yearReleased = request.form['yearReleased']
    film.rating = request.form['rating']
    film.duration = request.form['duration']
    film.genre = request.form['genre']
    # get today's date from function, above all the routes
    # film.updated = stringdate()

    form1 = AddRecord()
    if form1.validate_on_submit():
        # update database record
        db.session.commit()
        # create a message to send to the template
        message = f"The data for the film, {film.title} has been updated."
        return render_template('resultFF.html', message=message)
    else:
        # show validaton errors
        film.id = id
        # see https://pythonprogramming.net/flash-flask-tutorial/
        for field, errors in form1.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(form1, field).label.text,
                    error
                ), 'error')
        return render_template('edit_or_delete.html', form1=form1, film=film, choice='edit')


# +++++++++++++++++++++++
# error routes
# https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/#registering-an-error-handler

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', pagetitle="404 Error - Page Not Found", pageheading="Page not found (Error 404)", error=e), 404


@app.errorhandler(405)
def form_not_posted(e):
    return render_template('error.html', pagetitle="405 Error - Form Not Submitted", pageheading="The form was not submitted (Error 405)", error=e), 405


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', pagetitle="500 Error - Internal Server Error", pageheading="Internal server error (500)", error=e), 500

# +++++++++++++++++++++++


if __name__ == '__main__':
    app.run(debug=True)
