from flask import Flask
import sqlite3 as sql
app = Flask(__name__)


@app.route('/howmany',methods = ['POST', 'GET'])


@app.route('/list',methods = ['POST', 'GET'])
def list():
con = sql.connect("employees.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute("select * from employees")

   rows = cur.fetchall();

@app.route('/isinoffice',methods = ['POST', 'GET'])
