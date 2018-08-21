from datetime import datetime
from app import db
from app import login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_parent_user = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    accounts = db.relationship('Account', backref='owner', lazy='dynamic')

    def set_as_parent_user(self):
        self.is_parent_user = 1

    def set_parent_of_child(self, parent_id):
        self.is_parent_user = 0
        self.parent_id = parent_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Integer, default=0)
    name = db.Column(db.String(140))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')

    def __repr__(self):
        return '<Account {}>'.format(self.name)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, default=0)
    description = db.Column(db.String(140))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    def __repr__(self):
        return '<Transaction {}>'.format(self.description, self.amount)