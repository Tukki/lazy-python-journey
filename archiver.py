#_*_ coding: utf-8 _*_
import argparse
from BeautifulSoup import BeautifulSoup as Soup

from utils import build_opener
from auth import simulate_login
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

#构建连接器
opener = build_opener()

#尝试登录
success, gsid = simulate_login(opener, email, psw)
print 'success: ', success
print 'gsid   : ', gsid
print 'target : ', uid

from sqla_db import DBSaver, DumpSaver

saver = DBSaver(uid, debug=False)
dump = DumpSaver(uid)

def load_page(num):
    """
    load target page back
    """
    url = "http://weibo.cn/%s/profile?gsid=%s&page=%s" % (uid, gsid, num)
    r = opener.open(url)
    return r.read()

def archive_page(page, ignore=False):
    soup = Soup(page)
    mids = get_mids(soup.prettify())
    updated = False
    for mid in mids:
        data = parse_weibo(soup, mid)
        try:
            saver.save(data)
        except:
            if not ignore: 
                updated = True
                break
    #不在函数内递归,否则打印的错误信息太长了.
    current, total = get_page_info(soup)
    #TODO 这个信息放在这里返回毫无意义
    print "done page %s / %s" % (current, total)
    return current, total, updated


#def update(page):
#    """
#    顺序追加新信息.当出现插入重复则停止
#    """
#    parser = Parser(page)
#    for data in parser.get_weibo_data():
#        saver.save(data)
#        #if double, update done
#    return update 

per_page = 10
page = load_page(1)
soup = Soup(page)

#check remote and local
remote = get_weibo_count(page)
local = saver.get_count()

print remote, local
if remote > local:
    while True:
        c, t, updated= archive_page(page)
        if updated: break
        if c < t:
            page = load_page(c+1)
        else:
            break

#check remote and local
local = saver.get_count()
print local

if remote > local:
    #计算由哪一页开始. 没有余数才由下一页开始获取数据
    #TODO 还是有个问题.已更新的那部分有删除情况.会导致这里的计算错位
    quotien, remainer = divmod(local, per_page)
    num = remainer == 0 and (quotien + 1) or quotien
    print 'continue page %s' % num
    page = load_page(num)
    while True:
        c, t, updated = archive_page(page, ignore=True)
        if c < t:
            page = load_page(c+1)
        else:
            break
