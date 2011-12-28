#_*_ coding: utf-8 _*_
import argparse
from BeautifulSoup import BeautifulSoup as Soup

from utils import build_opener
from auth import simulate_login


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

s = Soup(r.read())

print s.prettify()
