from app import *

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()

import MySQLdb
import traceback

conn = MySQLdb.connect(user="root", db="honeypot")
cur = conn.cursor()
try:
    cur.execute('drop table admin_requests;')
except:
    traceback.print_exc()

cur.execute("""CREATE TABLE admin_requests (
         id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
         uri VARCHAR(1000),
         agent VARCHAR(1000)
       );""")
conn.close()
