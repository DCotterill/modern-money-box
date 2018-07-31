import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'if I could turn back time to the matrix'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://money-box:money@localhost/moneybox'
    SQLALCHEMY_TRACK_MODIFICATIONS = False