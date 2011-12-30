#_*_ coding: utf-8 _*_
#TODO logging
import argparse
from BeautifulSoup import BeautifulSoup as Soup

from auth import simulate_login
from utils import build_opener
from pageparse import *

#获取参数
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', help='user email')
parser.add_argument('-p', '--psw', help="password")
parser.add_argument('-t', '--target', help='target user ID')
args = parser.parse_args()

email = args.user
psw = args.psw
uid = args.target

class Loader(object):
    
    def __init__(self, opener=None):
        self.opener = opener or build_opener()

    def login(self, email, psw, remember=True):
        success, gsid = simulate_login(self.opener, email, psw, remember)
        self.gsid = gsid
        return success

    def set_target(self, uid):
        self._target_uid = uid

    def get_page(self, num):
        return self._load_page(num)

    def _load_page(self, num):
        url = "http://weibo.cn/%(uid)s/profile?gsid=%(gsid)s&page=%(page)s" % {'uid': self._target_uid, 'gsid': self.gsid, 'page': num}
        r = self.opener.open(url)
        page = r.read()
        return page


class Parser(object):
    def __init__(self, source):
        self.soup = Soup(source)
        self.source = source
        self._prettify= self.soup.prettify()

    def prettify(self):
        return self._prettify

    def get_total_weibo_count(self):
        return get_weibo_count(self._prettify)

    def get_page_weibo_count(self):
        return len(self.get_mids())    
    
    def get_mids(self):
        if not hasattr(self, '_mids'):
            self._mids = get_mids(self._prettify)
        return self._mids

    def is_valid(self):
        return len(self.get_mids()) > 0

    def get_page_info(self):
        return get_page_info(self.soup)

    def get_weibo(self, mid):
        return parse_weibo(self.soup, mid)


from sqla_db import DBSaver as Archiver

loader = Loader()

#登录
success = loader.login(email, psw)
print success
print loader.gsid

loader.set_target(uid)
#初始化保存
archiver = Archiver(uid, debug=False)

page = loader.get_page(1)
parser = Parser(page)

remote_count = parser.get_total_weibo_count()  #lock with this value durning archive

print 'remote count :', remote_count

while parser.is_valid():
    mids = parser.get_mids()
    created = False
    for mid in mids:
        weibo = parser.get_weibo(mid)
        created = archiver.save(weibo)
        if not created: break

    if not created: break
    current, total = parser.get_page_info()
    if current < total:
        page = loader.get_page(current + 1)
        parser = Parser(page)
    else:
        break

#now, update proccess finish
#remote_count should always great than or equal the archived_count
archived_count = archiver.get_count()
print 'archived_count :', archived_count

if archived_count == remote_count:
    exit()

if archived_count > remote_count:
    print 'WTF, I failed, AGAIN'
    exit()

quotient, remainer = divmod(archived_count, 10)
num = quotient + 1 #
cursur = 0

#TODO 此循环应该和上面那个循环逻辑一致.都是插入重复错误
page = loader.get_page(num)
parser = Parser(page)
while parser.is_valid():
    mids = parser.get_mids()
    created = False
    for mid in mids[cursur:]:
        weibo = parser.get_weibo(mid)
        created = archiver.save(weibo)
        #assert created
    current, total = parser.get_page_info()
    if current < total:
        page = loader.get_page(current + 1)
        parser = Parser(page)
    else:
        break

archived_count = archiver.get_count()
print 'archived_count :', archived_count

if archived_count == remote_count:
    exit()

elif archived_count > remote_count:
    print 'WTF, I failed, AGAIN'
    exit()

else:
    print 'my failed, miss some one'


"""
archived_count = archiver.get_weibo_count()

if archived_count == remote_count:
    archived success, exit


#try find out the page to continue archive
get page_num base on 10-per-page
parser for loader.get_page(page_num)
for weibo in parser:
    get unarchived_count 
if unarchived_count == parser.get_page_weibo_count():
    #all unarchived, try former page
    page_num -= 1 until 0
elif unarchived_count == 0:
    #all archived, try next page
    page_num += 1
else:
    #assert that the unarchived is not out of order
    now the page_num is the continue archive start page

"""
