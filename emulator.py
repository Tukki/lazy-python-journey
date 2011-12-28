#_*_ coding: utf-8 _*_
import re
import urllib
import urllib2
import cookielib

#用BeautifulStoneSoup会导致登录form获取错误
from BeautifulSoup import BeautifulSoup as Soup


SSO = "http://3g.sina.com.cn/prog/wapsite/sso/"
#注意,这里使用的是Http.没找到能使用https的简单页面
LOGIN_URL = SSO + "login.php"

class Emulator(object):

    def __init__(self):
        self.opener = build_opener()
        self._gsid = None

    def login(self, email, psw, remember=True):
        #获取手机版登录页,填写用户信息后模拟登录. 登录成功后停留在登录成功页
        return self._login_impl(email, psw, remember)

    def get_gsid(self):
        return self._gsid

    def _login_impl(self, email, psw, remember=True):
        login_page = self.opener.open(LOGIN_URL)
        soup = Soup(login_page.read())
        form = soup.find('form')
        update_form(form, user=email, psw=psw, remember=remember)
        submit_to = SSO + get_submit_action(form)
        submit_data = get_datas(form)
        
        print submit_to, submit_data
        response = self.opener.open(submit_to, urllib.urlencode(submit_data))
        
        self._gsid = parsing_gsid(response.read())
        print response.info().keys()
        return True

    def open(self, url):
        return self.opener.open(url)

#=== helpers =======
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



def get_utf8Attrs(elem):
    """ 
    BeautifulSoup的attrMap有时候会为None, 所以用attrs来构建
    """
    return dict([(a[0], a[1].encode('utf8')) for a in elem.attrs])


def update_form(form, user, psw, remember=True):
    """
    填写信息到登录表单
    """
    form.find('input', {'name': 'mobile'})['value'] = user
    #password的字段名和vk值有关
    form.find('input', {'type': 'password'})['value'] = psw
    #
    r = form.find('input', {'name': 'remember'})
    if remember:
        r['value'] = "on"
    else:
        r.extract()  #不记住直接移除


def get_submit_action(form):
    """获取form的目标地址.每次不同,其参数变化"""
    attrs = get_utf8Attrs(form)
    return attrs['action']


def get_datas(form):
    """获取form里面的值对. {name: value}"""
    datas = {}
    for input in form.findAll('input'):
        attrs = get_utf8Attrs(input)
        datas[attrs['name']] = attrs['value']
    return datas
   

def parsing_gsid(success_page):
    """
    原来用了Soup来解析.现在用正则式获取
    """
    pt = r"gsid=(\w+)&amp;"
    r = re.search(pt, success_page)
    assert r
    return r.group(1)

