from hashlib import md5
from datetime import datetime
from face_mash_app import db

  # id integer primary key autoincrement,
  # photo text not null,
  # elo double not null,
  # sex text not null,
  # times integer not null
USER_MAN = 1
USER_WOMAN = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(1024), unique=True)
    elo = db.Column(db.Float())
    sex = db.Column(db.Integer, default=USER_MAN)
    times = db.Column(db.Integer)

    def __init__(self, photo, sex=USER_MAN):
        self.photo = photo
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