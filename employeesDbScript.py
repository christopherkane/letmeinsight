from flask import Flask
from flask import request
import sqlite3 as sql
app = Flask(__name__)


@app.route('/howmany',methods = ['POST', 'GET'])
def howmany():
	con = sql.connect("employees.db")
	con.row_factory = sql.Row

	cur = con.cursor();
	cur.execute(COUNT(ALL,"select name from employees where inOffice = true")).fetchall()

	con.commit()
	con.close()

@app.route('/list',methods = ['POST', 'GET'])
def list():
	con = sql.connect("employees.db")
   	con.row_factory = sql.Row

   	cur = con.cursor()
   	cur.execute("select * from employees")

	con.commit()
	con.close()

@app.route('/isinoffice',methods = ['POST', 'GET'])
def isinoffice():
	user = request.args.get('user')
	con = sql.connect("employees.db")
   	con.row_factory = sql.Row

   	cur = con.cursor()
	cur.execute("select id from employees where name = ?", [user])
	
	con.commit()
	con.close()
