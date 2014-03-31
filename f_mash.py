import random
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Response
import os

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            schema = f.read()
            db.cursor().executescript(schema)
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select id, photo from users order by id desc')
    users = cur.fetchall()
    count_users = len(users)
    if count_users:
        u1 = random.randint(0, count_users-1)
        u2 = random.randint(0, count_users-1)
        return render_template('index.html', user1=users[u1], user2=users[u2])
    return render_template('index.html')


@app.route('/test')
def add_test():
    db = get_db()
    db.execute('insert into users (photo) values (?)', ["https://pp.vk.me/c311931/v311931047/7260/4NUmSFHBBcU.jpg"])
    db.execute('insert into users (photo) values (?)', ["https://pp.vk.me/c418719/v418719276/8452/173yVrN1-FE.jpg"])
    db.execute('insert into users (photo) values (?)', ["https://pp.vk.me/c313618/v313618569/77ee/3wbYr1x71II.jpg"])
    db.commit()
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run()
