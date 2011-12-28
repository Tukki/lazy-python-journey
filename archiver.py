#_*_ coding: utf-8 _*_
import argparse
from BeautifulSoup import BeautifulSoup as Soup

from utils import build_opener
from auth import simulate_login
from pageparse import *

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', help='user')
parser.add_argument('-p', '--psw', help="password")

args = parser.parse_args()

email = args.user
psw = args.psw

opener = build_opener()

success, gsid = simulate_login(opener, email, psw)
print 'success: ', success

print 'gsid: ', gsid

r = opener.open('http://www.weibo.cn?gsid='+gsid)

page = r.read()

s = Soup(page)
page = s.prettify()  
#print s.prettify()

mids =  get_mids(s.prettify())  #必需prettity()才能获取到
print mids


def dump_saver(datas):
    for k in datas.keys():
        print k, '', datas[k]
    print ''

for mid in mids:
    data = parse_weibo(s, mid)
    dump_saver(data)    

print get_page_info(s)


