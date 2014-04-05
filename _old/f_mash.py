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
    cur = db.execute('select id, photo from users order by elo desc')
    users = cur.fetchall()
    count_users = len(users)
    if count_users:
        u1 = random.randint(0, count_users - 1)
        # u1_neighs is [u1-eps ; u1+eps] C [0; count_users]
        epsilon = count_users ** (1 / 2)
        u1_neighs = users[max(0, u1 - epsilon):max(0, u1)] + users[min(u1 + 1, count_users):min(u1 + 1 + epsilon,
                                                                                                count_users)]
        u2 = random.randint(0, len(u1_neighs) - 1)
        return render_template('index.html', user1=users[u1], user2=u1_neighs[u2])
    return render_template('index.html')


def elo(Wa, Ra, Rb, times):
    """ (int)Wa = 1 if a is winner else 0
        (float)Ra - elo rate of a
        (float)Rb - elo rate of b
        (int)K - coeff depends on Ra and times
    """
    Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
    if Ra > 2000:
        K = 10
    elif times > 30:
        K = 15
    else:
        K = 30
    return Ra + K * (Wa - Ea)


@app.route('/vote', methods=["POST"])
def vote():
    db = get_db()
    win_id = request.form["win_id"]
    cur = db.execute('select elo, times from users where id = %s' % (win_id))
    win_elo, win_times = cur.fetchall()[0]

    lose_id = request.form["lose_id"]
    cur = db.execute('select elo, times from users where id = %s' % (lose_id))
    lose_elo, lose_times = cur.fetchall()[0]

    #print "WIN Id%s, rate=%s, %s times" % (win_id, win_elo, win_times)
    #print "LOSE Id%s, rate=%s, %s times" % (lose_id, lose_elo, lose_times)

    win_elo = elo(1, float(win_elo), float(lose_elo), int(win_times))
    lose_elo = elo(0, float(lose_elo), float(win_elo), int(lose_times))

    db.execute('update users set elo = %f, times = %d where id = %s' % (win_elo, int(win_times) + 1, win_id))
    db.execute('update users set elo = %f, times = %s where id = %s' % (lose_elo, lose_times, lose_id))
    db.commit()

    #print "WIN new rate=%f" % (win_elo)
    #print "LOSE new rate=%f" % (lose_elo)

    return redirect('/')


@app.route('/top')
def top():
    TOP_N = 10
    db = get_db()
    cur = db.execute('select photo from users order by elo desc')
    tops = cur.fetchall()

    TOP_N = min(TOP_N, len(tops))

    return render_template('top.html', tops=tops[:TOP_N], n=TOP_N)


@app.route('/test')
def add_test():
    db = get_db()
    # db.execute('insert into users (photo, elo, times) values (?, ?, ?)',
    #            ["https://pp.vk.me/c311931/v311931047/7260/4NUmSFHBBcU.jpg", 400.0, 0])
    # db.execute('insert into users (photo, elo, times) values (?, ?, ?)',
    #            ["https://pp.vk.me/c418719/v418719276/8452/173yVrN1-FE.jpg", 400.0, 0])
    # db.execute('insert into users (photo, elo, times) values (?, ?, ?)',
    #            ["https://pp.vk.me/c313618/v313618569/77ee/3wbYr1x71II.jpg", 400.0, 0])

    with open("../photos.txt") as file:
        for photo in file:
            db.execute('insert into users (photo, elo, times) values (?, ?, ?)', [photo, 400.0, 0])

    db.commit()
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0')
