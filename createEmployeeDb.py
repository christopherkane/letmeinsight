#!/usr/bin/python

import sqlite3

USERS = [
  ('Christopher Kane', 'christopher_kane@rapid7.com'),
  ('Iain Wilson', 'iain_wilson@rapid7.com'),
  ('Conor McAteer', 'conor_mcateer@rapid7.com'),
  ('Connor Knox', 'connor_knox@rapid7.com'),
  ('Scott Devlin', 'scott_devlin@rapid7.com'),
  ('Nick Mifsud', 'nick_mifsud@rapid7.com'),
  ('Arnaud Roger', 'arnaud_roger@rapid7.com'),
  ('Chris Laughlin', 'chris_laughlin@rapid7.com')
]

INSERT = '''
INSERT INTO employees(name,email)
  VALUES(?,?)
'''

database = 'employees.db'

# create a database connection
conn = sqlite3.connect(database)
print('Opened database successfully');

conn.execute('CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, email TEXT, inOffice BOOLEAN DEFAULT 0)')
print('Table created successfully');

for user in USERS:
    print('Inserting: ' + user[0])
    conn.execute(INSERT, user)

conn.commit()
conn.close()
