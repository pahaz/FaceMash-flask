import random
from flask import render_template, flash, redirect, session, url_for, request, g
# from flask.ext.login import login_user, logout_user, current_user, login_required
# from app import app, db, lm, oid
from face_mash_app import app, db
# from forms import LoginForm, EditForm
from models import User, Vote
from datetime import datetime
from models import USER_MAN, USER_WOMAN


@app.route('/')
def index():
    # cur = db.engine.execute('select id, photo from user order by elo desc')
    users = User.query.all()
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
    win_id = request.form["win_id"]
    win = User.query.get(win_id)
    win_elo, win_times = win.elo, win.times

    lose_id = request.form["lose_id"]
    lose = User.query.get(lose_id)
    lose_elo, lose_times = lose.elo, lose.times

    #print "WIN Id%s, rate=%s, %s times" % (win_id, win_elo, win_times)
    #print "LOSE Id%s, rate=%s, %s times" % (lose_id, lose_elo, lose_times)

    win_elo = elo(1, float(win_elo), float(lose_elo), int(win_times))
    lose_elo = elo(0, float(lose_elo), float(win_elo), int(lose_times))

    win.elo = win_elo
    win.times += 1

    lose.elo = lose_elo
    lose.times += 1

    db.session.commit()
    #print "WIN new rate=%f" % (win_elo)
    #print "LOSE new rate=%f" % (lose_elo)

    return redirect('/')


@app.route('/top')
def top():
    TOP_N = 10
    cur = db.engine.execute('select photo from user order by elo desc')
    tops = cur.fetchall()

    TOP_N = min(TOP_N, len(tops))

    return render_template('top.html', tops=tops[:TOP_N], n=TOP_N)


@app.route('/test')
def add_test():
    user = User("https://pp.vk.me/c311931/v311931047/7260/4NUmSFHBBcU.jpg")
    db.session.add(user)
    user = User("https://pp.vk.me/c418719/v418719276/8452/173yVrN1-FE.jpg")
    db.session.add(user)

    with open("male_photo.txt") as file:
        for photo in file:
            user = User(photo, USER_MAN)
            db.session.add(user)

    with open("female_photo.txt") as file:
        for photo in file:
            user = User(photo, USER_WOMAN)
            db.session.add(user)

    db.session.commit()
    return redirect('/')