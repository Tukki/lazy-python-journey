#_*_ coding: utf-8 _*_

import argparse

from sqlalchemy import create_engine
from sqlalchemy.sql import select, func

from sqla_db import items

parser = argparse.ArgumentParser()
parser.add_argument('--db', help='db name')

args = parser.parse_args()
name = args.db

url = "sqlite:///%s" % name

engine = create_engine(url)

conn = engine.connect()

query = select([func.count(items.c.mid)])
count = conn.execute(query).fetchone()[0]

print 'saved item :', count
print ''

query = select([items.c.mid, items.c.text]).offset(count-1).limit(1)
result = conn.execute(query).fetchall()

for r in result:
    print r.mid
    print r.text
    print ""

conn.close()


