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

    def get_total_page_count(self):
        return get_page_info(self.soup)[1]

    def get_weibo(self, mid):
        return parse_weibo(self.soup, mid)

    def parsing_weibo(self):
        for mid in self.get_mids():
            yield self.get_weibo(mid)

    def had_next_page(self):
        current, total = self.get_page_info()
        return current < total


from sqla_db import DBSaver as Archiver

def create_page_parser(num):
    page = loader.get_page(num)
    return Parser(page)

def archive_page(start, end, is_update=False):
    current_page_num = start
    archived_count = 0
    while True:
        parser = create_page_parser(current_page_num)

        if not parser.is_valid():
            print 'the page is not valid'
            return False, archived_count
        
        for weibo in parser.parsing_weibo():
            created = archiver.save(weibo)
            
            if created:
                archived_count += 1
            elif not is_update:
                print 'double archive'
                return False, archived_count
            else:
                print 'update success'
                return True, archived_count
        
        print 'page %s / %s done, added %s new entries until now' % (current_page_num, end, archived_count)

        if current_page_num < end:
            current_page_num += 1
        else:
            return True, archived_count


def fix_continue_archived_page(archived_count, end_page, prepage=10):
    fixing_page = archived_count / 10 + 1  #如果不修正,返回这个能应付一般情况了
    #start fixed
    fixed_count = 0
    formward_checked = False
    afterward_checked = False
    while True:
        print 'checking page ', fixing_page
        parser = create_page_parser(fixing_page)
        #TODO 需保证页面有效
        assert parser.is_valid()
        
        #获取当前页有多少时已存储的
        mids = parser.get_mids()
        exist_count = 0
        for mid in mids:
            is_exist = archiver.check_exist(mid)
            if is_exist:
                exist_count += 1

        page_weibo_count = parser.get_page_weibo_count()

        if exist_count == page_weibo_count:
            if not afterward_checked:
                #本页都已备份,但下一页未检测,尝试下一页
                fixing_page += 1
                formward_checked = True
            else:
                #下页已检查,修正完毕
                fixing_page += 1
                break
        elif exist_count == 0:
            if not formward_checked:
                fixing_page -= 1
                afterward_checked = True
            else:
                #上一页已检测,这页全没备份. 修正完毕
                break
        else:
            #修正当前页
            for weibo in parser.parsing_weibo():
                created = archiver.save(weibo)
                #重复忽略
                if created:
                    fixed_count += 1
            assert fixed_count + exist_count == page_weibo_count
            fixing_page += 1
            break
        #越界
        if fixing_page == 0 or fixing_page > end_page:
            break
    return fixing_page, fixed_count




loader = Loader()

#登录
success = loader.login(email, psw)
print success
print loader.gsid

loader.set_target(uid)
#初始化保存
archiver = Archiver(uid, debug=False)

parser = create_page_parser(1)

remote_count = parser.get_total_weibo_count()  #TODO lock with this value durning archive
total_page = parser.get_total_page_count()

archived_count = archiver.get_count()

print 'remote count :', remote_count
print 'remote page count: ', total_page
print 'archived_count :', archived_count

is_success, archived_count = archive_page(start=1, end=total_page, is_update=True)
print 'update success :', is_success
print 'update count :', archived_count

if not is_success:
    print 'update failed'
    exit()

#now, update proccess finish
#XXX Fuck. will be delete remote_count should always great than or equal the archived_count
archived_count = archiver.get_count()
print 'archived_count :', archived_count


continue_page, fixed_count = fix_continue_archived_page(archived_count, total_page)
print 'fixed archived %s' % fixed_count

print 'continue_page is ', continue_page

archived_count = archiver.get_count()
print 'archived_count :', archived_count

if archived_count == remote_count:
    exit()

elif archived_count > remote_count:
    print 'WTF, I failed, AGAIN'
    exit()

if continue_page == total_page:
    print 'archived done'
    exit()

#开始追加未保存的页面
is_success, archived_count = archive_page(start=continue_page, end=total_page, is_update=False)

print 'update success :', is_success
print 'update count :', archived_count

archived_count = archiver.get_count()

print 'remote weibo count is ', remote_count
print 'archived weibo count is ', archived_count




