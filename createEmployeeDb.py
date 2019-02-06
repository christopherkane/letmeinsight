#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('employees.db')

print('Opened database successfully');

conn.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, email TEXT, inOffice BOOLEAN)')

print('Table created successfully');

conn.close()
