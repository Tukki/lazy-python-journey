#_*_ coding: utf-8 _*_

from sqlalchemy import create_engine, MetaData
from sqlalchemy import (Table, Column, String, BigInteger, 
                        Boolean, DateTime)
from sqlalchemy.sql import func, select
from sqlalchemy.exc import IntegrityError


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

    def save(self, data):
        conn = self.engine.connect()  #TODO 问题应该出现在这.每次写入都开闭开闭的,低效
        try:
            ins = items.insert()
            conn.execute(ins, **data)
            created = True
        except IntegrityError:
            created = False
        finally:
            conn.close()
        return created

    def get_count(self):
        conn = self.engine.connect()
        s = select([func.count(items.c.mid)])
        count = conn.execute(s).fetchone()[0]
        conn.close()
        return count


class DumpSaver(object):
    def __init__(self, name, debug=True):
        pass

    def save(self, data):
        for k in data.keys():
            print k, ': ', data[k]
        print ''

