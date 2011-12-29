#_*_ coding: utf-8 _*_
import argparse
from BeautifulSoup import BeautifulSoup as Soup

from utils import build_opener
from auth import simulate_login
from pageparse import *

#获取参数
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', help='user')
parser.add_argument('-p', '--psw', help="password")
args = parser.parse_args()

email = args.user
psw = args.psw

#构建连接器
opener = build_opener()

#尝试登录
success, gsid = simulate_login(opener, email, psw)
print 'success: ', success
print 'gsid   : ', gsid

from sqla_db import DBSaver, DumpSaver

saver = DBSaver('test', debug=False)
dump = DumpSaver('test')

#TODO 简单点,先让用户自己填写需要的目标id算了.还没有找到
uid = "2214658753"
#uid = "1813080181"

def load_page(num):
    """
    load target page back
    """
    url = "http://weibo.cn/%s/profile?gsid=%s&page=%s" % (uid, gsid, num)
    r = opener.open(url)
    return r.read()

def archive_page(page_num):
    page = load_page(page_num)
    soup = Soup(page)
    mids = get_mids(soup.prettify())
    updated = False
    for mid in mids:
        data = parse_weibo(soup, mid)
        #dump.save(data)
        saver.save(data)
    #    if not success:
    #        updated = True
    #        break
    #if updated:
    #    check_and_start_archive()
    #else:
    #    if not the the last page:
    #        go archive next page 
    #    if is the last page 
    #        done, archive done
    #TODO 这种函数内递归,导致打印的错误信息太长了.
    current, total = get_page_info(soup)
    print "done page %s / %s" % (current, total)

    #if current < total:
    #    archive_page(current + 1)
    return current, total


num = 1
while True:
    current, total = archive_page(num)
    if current < total:
       num = current + 1
    else:
        break

print 'count', saver.get_count()

#def start_archive():
#   page = load_first_page()
#   total_count = get_weibo_total_count(page)
#   archived_count = get_archived_count()
  

#def check_status():
#   total_count
#   archived_count
#   if total_count > archived_count:
#       find out the start page num
#       archive_page with ignore had_saved
#   elif total_count < archived_count:
#       maybe I failed, maybe you delete some bo
#   else:
#       done 

#def continue_archive():
#   get total count
#   get archived count

    
