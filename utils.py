#_*_ coding: utf-8 _*_
import re
import urllib
import urllib2
import cookielib

_headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Connection": "keep-alive",
}


def build_opener():
    #TODO cookie好像不生效
    cj = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cj)
    redirect_handler = urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(cookie_handler, redirect_handler)
    opener.addheaders = zip(_headers.keys(), _headers.values())  #使每次都追加这些信息
    return opener

