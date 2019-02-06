#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('employees.db')

print "Opened database successfully";

conn.execute('CREATE TABLE employees (name TEXT, email TEXT, inOffice INTEGER)')

print "Table created successfully";

conn.close()
