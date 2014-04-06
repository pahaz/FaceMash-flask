#!/usr/bin/env python
# -*- coding: cp1251 -*-
from hashlib import md5
from datetime import datetime
from face_mash_app import db
import requests as r
import re

  # id integer primary key autoincrement,
  # photo text not null,
  # elo double not null,
  # sex text not null,
  # times integer not null
USER_MAN = 1
USER_WOMAN = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vk_id = db.Column(db.Integer)
    photo = db.Column(db.String(1024), unique=True)
    elo = db.Column(db.Float())
    sex = db.Column(db.Integer, default=USER_MAN)
    times = db.Column(db.Integer)

    def __init__(self, vk_id, photo, sex=USER_MAN):
        self.photo = photo
        self.vk_id = vk_id
        self.sex = sex
        self.times = 0
        self.elo = 400.0

    def __repr__(self):
        return '<User %r>' % (self.id, )


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(16))
    timestamp = db.Column(db.DateTime)
    win_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lose_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, request, win_id, lose_id):
        self.win_id = win_id
        self.lose_id = lose_id
        self.ip = request.remote_addr
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<Vote %r>' % (self.id, )

region_checker = re.compile(r'(<region>)(.+?)(</region>)', re.UNICODE)

class IpAddress(db.Model):
    ip = db.Column(db.String(16), primary_key=True, unique=True)
    correct = db.Column(db.Integer)

    def __init__(self, request):
        self.ip = request.remote_addr

        if self.ip[:2] != "10":
            checker_url = 'http://ipgeobase.ru:7020/geo?ip=' + self.ip

            try:
                xml_txt = r.get(checker_url, timeout=5.0).text
                match_obj = re.search(region_checker, xml_txt)
                if not match_obj:
                    self.correct = 0
                elif match_obj.group(2) == u"Свердловская область":
                    self.correct = 1
            except r.Timeout:
                print "TIMEOUT"
        else:
            self.correct = 1

    def __repr__(self):
        return '<IpAddress %r>' % (self.id, )
