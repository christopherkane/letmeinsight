from flask import Flask, g, request, jsonify
import sqlite3 as sql
app = Flask(__name__)
app.debug = True


@app.route('/howmany', methods=["POST","GET"])
def howmany():
    con = sql.connect("employees.db")

    cur = con.cursor()
    cur.execute("SELECT count(name) FROM employees WHERE inOffice = 1")
    data = cur.fetchall()

    con.commit()
    con.close()
    return jsonify(data)


@app.route('/list', methods=["POST","GET"])
def list():
    con = sql.connect("employees.db")

    cur = con.cursor()
    cur.execute("SELECT * FROM employees WHERE inOffice = 1")

    response = []

    for row in cur.fetchall():
        response.append({ "text": row[1] })

    con.commit()
    con.close()

    return jsonify({
		"text": "The following people are in the office",
		"attachments": response
	})

@app.route('/isinoffice', methods=["POST","GET"])
def isinoffice():
    con = sql.connect("employees.db")
    employee_name = request.args.get('name')

    cur = con.cursor()
    cur.execute("SELECT inOffice FROM employees WHERE name = ?", [employee_name])
    data = cur.fetchall()

    con.commit()
    con.close()
    return jsonify(data)
