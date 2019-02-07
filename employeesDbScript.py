from flask import Flask, g, request, jsonify
import sqlite3 as sql
app = Flask(__name__)
app.debug = True


@app.route('/howmany', methods=["POST","GET"])
def howmany():
    con = sql.connect("employees.db")

    cur = con.cursor()
    cur.execute("SELECT count(name) FROM employees WHERE inOffice = 1")
    number = cur.fetchone()[0]

    con.commit()
    con.close()

    return "The number of people in the office is: " + str(number)


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

@app.route('/isinoffice', methods=["POST"])
def isinoffice():
    command = request.form['command']
    employee_name = request.form['text']

    con = sql.connect("employees.db")
    cur = con.cursor()
    cur.execute("SELECT inOffice FROM employees WHERE name = ?", [employee_name])
    row = cur.fetchone()
    response = ""

    if row is None:
        response = ":thinking_face: Who is " + employee_name + "? Check the P45s issued"
    else:
        inOffice = row[0]
        emoji = ":ok_hand:" if inOffice else ":man-shrugging:"

        response = emoji + " " + employee_name + " is" + (" not" if not inOffice else "") + " in the office"

    con.commit()
    con.close()

    return jsonify({
		"text": response
	})
