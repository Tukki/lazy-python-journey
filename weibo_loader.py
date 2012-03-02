#_*_ coding: utf-8 _*_
import urllib
import urllib2
import cookielib

from page_parser import *

CHROME_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "deflate,sdch",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
}

def build_browser(headers=None):
    headers = headers or CHROME_HEADER  
    cj = cookielib.CookieJar()   #TODO this... maybe no work
    cookie_handler = urllib2.HTTPCookieProcessor(cj)
    redirect_handler = urllib2.HTTPRedirectHandler()
    browser = urllib2.build_opener(cookie_handler, redirect_handler)
    browser.addheaders = zip(headers.keys(), headers.values())
    return browser

_WEIBO_SSO = "http://3g.sina.com.cn/prog/wapsite/sso/"
_WEIBO_LOGIN_URL = _WEIBO_SSO + "login.php"

class WeiboLoader(object):
    
    def __init__(self, brower=None):
        self.brower = brower or build_browser()
        self.gsid = ""

    @property
    def is_logined(self):
        return self.gsid and True or False

    def login(self, email, psw):
        login_page = self.brower.open(_WEIBO_LOGIN_URL).read()
        action, values = parse_login_form(login_page)
        values = update_form_values(values, email, psw)
        
        submit_to = _WEIBO_SSO + action
        response = self.brower.open(submit_to, urllib.urlencode(values))
        success_page = response.read()
        self.gsid = parse_gsid(success_page)
        return self.is_logined

    def load_page(self, page_number):
        pass
