import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'WorkoutApp.db'),
    DEBUG=True,
    SECRET_KEY='development key ',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:  # Opens the schema file and runs it as a script
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):  # g is imported from flask
        g.sqlite_db = connect_db()  # says that if sqlite exists, connect it to database.
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_home():
    return render_template('homepage.html')

@app.route('/about')
def show_about():
    return render_template('about.html')

@app.route('/grammar')
def show_grammar():
    return render_template('grammarPage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/create', methods=['POST'])  # Create account
def create():
    db = get_db()
    cur = db.execute('SELECT username from profile where username=?',
                     [request.form['email']])
    row = cur.fetchone()
    if row is None:
        password = request.form['password']
        hPassword = generate_password_hash(password)
        db.execute('INSERT into profile (username, hPassword) values(?,?,)',
                   [request.form['first_name'], request.form['last_name'], request.form['email'], hPassword])
        db.commit()
        flash('You created an account!')
        return redirect(url_for('viewLogin'))
    else:
        flash('Email already taken')
        return redirect(url_for('viewCreateAccount'))

@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    cur = db.execute('SELECT hPassword, id from profile where username=?',
                     [request.form['username']])
    row = cur.fetchone()
    if row is None:
        flash('Invalid username')
        return redirect(url_for('login'))
    elif check_password_hash(row[0], request.form['password']):  # Not correct
        session['user_id'] = row[1]
        db = get_db()
        db.execute('UPDATE profile SET login=1 WHERE id=?',
                   [session['user_id']])
        db.commit()
        flash('You were logged in')
        return redirect(url_for('homeIn'))
    else:
        flash('Invalid password')
        return redirect(url_for('viewLogin'))