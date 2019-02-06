from flask import Flask, g, request, jsonify
import sqlite3 as sql
app = Flask(__name__)
app.debug = True


@app.route('/howmany')
def howmany():
    con = sql.connect("employees.db")

    cur = con.cursor()
    cur.execute("SELECT count(name) FROM employees WHERE inOffice = true")
    data = cur.fetchall()

    con.commit()
    con.close()
    return jsonify(data)


@app.route('/list')
def list():
    con = sql.connect("employees.db")

    cur = con.cursor()
    cur.execute("SELECT * FROM employees")
    data = cur.fetchall()

    con.commit()
    con.close()
    return jsonify(data)

@app.route('/isinoffice/<user>/')
def isinoffice(user=None):
    con = sql.connect("employees.db")
    user = request.args.get('user')

    cur = con.cursor()
    cur.execute("SELECT inOffice FROM employees WHERE email = ?", [user])
    data = cur.fetchall()

    con.commit()
    con.close()
    return jsonify(data)
