# -*- coding: utf-8 -*-

from app import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time, traceback, random, string

main_url = "http://localhost:5000/"

with app.app_context():
    ids = [exploit.id for exploit in Exploit.query.filter(Exploit.is_read == 0)]


print ids

with open("key.txt") as f:
    key = f.read().strip()

driver = webdriver.Firefox()
driver.set_page_load_timeout(10)

for exp_id in ids:
    print exp_id
    try:
        otp = ''.join(random.choice(string.ascii_letters) for i in xrange(30))
        sign = sha256(key + otp).digest()
        driver.get(main_url + "viewexploit/{}/?otp={}&sign={}".format(exp_id, otp.encode('hex'), sign.encode('hex')))
        time.sleep(5)
        with app.app_context():
            exp = Exploit.query.filter_by(id=exp_id).first()
            exp.is_read = True
            db.session.add(exp)
            db.session.commit()
        driver.close()
    except:
        traceback.print_exc()
        try:
            driver.close()
        except:
            pass
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(10)
