#_*_ coding: utf-8 _*_

from sqlalchemy import create_engine, MetaData
from sqlalchemy import (Table, Column, String, BigInteger, 
                        Boolean, DateTime)

metadata = MetaData()

items = Table('items', metadata, 
              Column('mid', String, unique=True),
              Column('text', String),
              Column('image', String),
              Column('time', String),
              Column('source', String),
              Column('is_retweet', Boolean),
              Column('rt_user', String),
              Column('rt_text', String),
             )

class DBSaver(object):
    def __init__(self, name, debug=False):
        url = "sqlite:///%s.db" % name
        self.engine = create_engine(url, echo=debug)
        metadata.create_all(bind=self.engine)
        self.conn = self.engine.connect()

    def save(self, data):
        ins = items.insert()
        self.conn.execute(ins, **data)


class DumpSaver(object):
    def __init__(self, name, debug=True):
        pass

    def save(self, data):
        for k in data.keys():
            print k, ': ', data[k]
        print ''

