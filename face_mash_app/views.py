#!/usr/bin/env python
# -*- coding: cp1251 -*-
import random, math, re
from flask import render_template, flash, redirect, session, url_for, request, g
# from flask.ext.login import login_user, logout_user, current_user, login_required
# from app import app, db, lm, oid
from face_mash_app import app, db
# from forms import LoginForm, EditForm, constants
from models import User, Vote, IpAddress, USER_MAN, USER_WOMAN
from datetime import datetime
import requests as r

from flask import jsonify

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


@app.route('/')
def index():

    def _find(lst, el):
        for i in range(len(lst)):
            if el == lst[i].id:
                return i

    users = User.query.order_by(User.elo).all()
    count_users = len(users)

    if count_users:
        votes_list = Vote.query.filter_by(ip=request.remote_addr).all()
        # Использованные id для этого IP
        used_ids = {vote.win_id for vote in votes_list} | \
            {vote.lose_id for vote in votes_list}
        # Неиспользованные id для этого IP
        good_ids = set(xrange(1, count_users)) - used_ids

        #print(used_ids)

        if len(good_ids) < 3:
            print "TIME TO DROP ids for this IP"

        u1 = random.choice(list(good_ids))

        # Эпсилон-окрестность (выколотая) из близких по рейтингу user-ов к u1
        epsilon = int(math.log(count_users, 2))
        eps_okrestnost = (  # Левая полуокрестность + Правая полуокрестность
            set(users[max(0, _find(users, u1) - epsilon):max(0, _find(users, u1))]) | 
            set(users[min(_find(users, u1) + 1, count_users):min(_find(users, u1) + 1 + epsilon, count_users)])
        )
        not_used_eps_okrestnost = eps_okrestnost & good_ids

        # Если в окрестности не осталось неиспользованных, зарандомь
        if len(not_used_eps_okrestnost) == 0:
            u2 = random.choice(list(good_ids - {u1}))
        else:
            u2 = random.choice(list(not_used_eps_okrestnost))

        # Найти User-obj по id
        u1, u2 = User.query.get(u1), User.query.get(u2)
        return render_template('index.html', user1=u1, user2=u2)
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

    ipaddr = IpAddress.query.get(request.remote_addr)
    if not ipaddr:
        ipaddr = IpAddress(request)
        db.session.add(ipaddr)
        db.session.commit()

    if not ipaddr.correct:
        print "INCORRECT IP " + request.remote_addr
        return redirect('/')

    votes_list = Vote.query.filter_by(ip=request.remote_addr).all()
    # Использованные id для этого IP
    used_ids = {vote.win_id for vote in votes_list} | \
        {vote.lose_id for vote in votes_list}

    win_id = request.form["win_id"]
    lose_id = request.form["lose_id"]
    
    if (int(win_id) in used_ids) or (int(lose_id) in used_ids):
        return redirect('/anti-bot')

    win = User.query.get(win_id)
    lose = User.query.get(lose_id)
    if (not win) or (not lose):  # Id out of range
        return redirect('/')
    win_elo, win_times = win.elo, win.times
    lose_elo, lose_times = lose.elo, lose.times

    #print "WIN Id%s, rate=%s, %s times" % (win_id, win_elo, win_times)
    #print "LOSE Id%s, rate=%s, %s times" % (lose_id, lose_elo, lose_times)

    win_elo = elo(1, float(win_elo), float(lose_elo), int(win_times))
    lose_elo = elo(0, float(lose_elo), float(win_elo), int(lose_times))

    win.elo = win_elo
    win.times += 1

    lose.elo = lose_elo
    lose.times += 1

    vote = Vote(request, win_id, lose_id)
    db.session.add(vote)

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
    user = User(1, "https://pp.vk.me/c311931/v311931047/7260/4NUmSFHBBcU.jpg")
    db.session.add(user)

    with open("data\\male_photo.txt") as file:
        for item in file:
            item = item.split()
            user = User(int(item[0]), item[1][:-1] if item[1][-1] == '\n' else item[1], USER_MAN)
            db.session.add(user)

    with open("data\\female_photo.txt") as file:
        for item in file:
            item = item.split()
            user = User(int(item[0]), item[1][:-1] if item[1][-1] == '\n' else item[1], USER_WOMAN)
            db.session.add(user)

    db.session.commit()
    return redirect('/')

@app.route('/anti-bot')
def antibot():
    return render_template('fuck_you_bot.html', ip=request.remote_addr)
