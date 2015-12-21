# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
import datetime
from flask import Flask, request, render_template, redirect, Response
from hashlib import sha256
import MySQLdb

db = SQLAlchemy()

class Exploit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    is_read = db.Column(db.Boolean)
    def __init__(self, text):
        self.text = text
        self.is_read = False

class OneTimePassword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password =  db.Column(db.String(500), index=True, unique=True)
    def __init__(self, password):
        self.password = password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://honeypot@localhost/honeypot?charset=utf8&use_unicode=0'
app.debug = False
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    exploit_sent = False
    if request.method == "POST" and 'exploit' in request.form:
        exploit = Exploit(request.form['exploit'])
        db.session.add(exploit)
        db.session.commit()
        exploit_sent = True
    return render_template('index.html', exploit_sent=exploit_sent)


def check_otp():
    try:
        if not request.args.has_key('otp'):
            return u'Нужен одноразовый пароль'

        if len(request.args.get('otp')) > 500:
            return u'Одноразовый пароль слишком длинный'

        if not request.args.has_key('sign'):
            return u'Одноразовый пароль не подписан'

        key = open("key.txt").read().strip()
        otp = request.args['otp']
        sign = request.args['sign']
        if sha256(key + otp.decode('hex')).digest() != sign.decode('hex'):
            return u'Подпись неверная'

        if OneTimePassword.query.filter_by(password=otp).first():
            return u'Одноразовый пароль уже использован'

        db.session.add(OneTimePassword(otp))
        db.session.commit()
        log_admin_request()
    except:
        return u'Одноразовый пароль или подпись некорректны'

@app.route("/last_admin_requests/")
def last_admin_requests():
    error = check_otp()
    if error:
        return render_template('error.html', error=error)
    requests = get_last_admin_requests()
    return render_template("requests.html", requests=requests)

@app.route('/viewexploit/<id>/')
def viewexploit(id):
    error = check_otp()
    if error:
        return render_template('error.html', error=error)
    exploit = Exploit.query.filter_by(id=id).first_or_404()
    return render_template("exploit.html", exploit=exploit)

def log_admin_request():
    conn = MySQLdb.connect(user="honeypot", db="honeypot")
    query = 'insert into admin_requests (agent, uri) values ("{}", "{}");'.format(request.headers.get('User-Agent'), request.url)
    conn.cursor().execute(query, ())
    conn.commit()
    conn.close()

def get_last_admin_requests():
    conn = MySQLdb.connect(user="honeypot", db="honeypot")
    cur = conn.cursor()
    cur.execute('select uri, agent from admin_requests order by id desc limit 10')
    requests = cur.fetchall()
    conn.close()
    return requests

if __name__ == "__main__":
    app.run()
