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
current_page, total_page = parser.get_page_info()

print 'remote count :', remote_count
archived_count = archiver.get_count()
print 'archived_count :', archived_count


while parser.is_valid():
    mids = parser.get_mids()
    print len(mids)
    counter = 0
    created = False
    for mid in mids:
        weibo = parser.get_weibo(mid)
        created = archiver.save(weibo)
        if not created: break
        counter += 1
    if not created: break
    assert counter == len(mids)
    current, total = parser.get_page_info()
    print 'done page %s / %s' % (current, total)
    if current < total:
        page = loader.get_page(current + 1)
        parser = Parser(page)
    else:
        break

#TODO 如果是parser.is_valid()出错,应该中断. 现在的机制没处理这个自动重试了
if not parser.is_valid():
    print 'network failed, try it later'
    exit()

#now, update proccess finish
#remote_count should always great than or equal the archived_count
archived_count = archiver.get_count()
print 'archived_count :', archived_count

if archived_count == remote_count:
    exit()

if archived_count > remote_count:
    print 'WTF, I failed, AGAIN'
    exit()

continue_page = archived_count / 10 + 1

former_checked = False
afeter_checked = False
while continue_page > 0 and continue_page <= total_page:
    print 'checking page ', continue_page
    page = loader.get_page(continue_page)
    parser = Parser(page)

    assert parser.is_valid()

    mids = parser.get_mids()
    exist_count = 0
    for mid in mids:
        is_exist = archiver.check_exist(mid)
        if is_exist: exist_count += 1

    current_page_weibo_count = parser.get_page_weibo_count()
    if exist_count == current_page_weibo_count and not afeter_checked:
        #本页的都已经备份, 且下页没为检测.尝试下一页
        continue_page += 1
        former_checked = True
    elif exist_count == 0 and not former_checked:
        #本页的都没备份,且不是前一页来的
        continue_page -= 1
        afeter_checked = True
    else:
        #本页部分备份或在前页全备份,本页无备份.备份此页.下一页全新开始
        created_count = 0
        for mid in mids:
            weibo = parser.get_weibo(mid)
            created = archiver.save(weibo)
            if created: 
                created_count += 1
        assert created_count + exist_count == current_page_weibo_count
        continue_page += 1
        break


print 'continue_page is ', continue_page

archived_count = archiver.get_count()
print 'archived_count :', archived_count

if archived_count == remote_count:
    exit()

elif archived_count > remote_count:
    print 'WTF, I failed, AGAIN'
    exit()


#TODO 此循环应该和上面那个循环逻辑一致.都是插入重复错误
page = loader.get_page(continue_page)
parser = Parser(page)
while parser.is_valid():
    mids = parser.get_mids()
    created = False
    for mid in mids:
        weibo = parser.get_weibo(mid)
        created = archiver.save(weibo)
        #assert created
    current, total = parser.get_page_info()
    print 'done page %s / %s' % (current, total)
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
