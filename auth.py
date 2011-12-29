#_*_ coding: utf-8 _*_
import re
import urllib

#用BeautifulStoneSoup会导致登录form获取错误
from BeautifulSoup import BeautifulSoup as Soup

SSO = "http://3g.sina.com.cn/prog/wapsite/sso/"
#注意,这里使用的是Http.没找到能使用https的简单页面
LOGIN_URL = SSO + "login.php"


def simulate_login(opener, email, psw, remember=True):
    #获取手机版登录页,填写用户信息后模拟登录. 登录成功后停留在登录成功页
    #获取登录页面
    response = opener.open(LOGIN_URL)
    login_page = response.read()

    #填写表格
    form = Soup(login_page).find('form')
    update_form(form, user=email, psw=psw, remember=remember)
    #登录
    submit_to = SSO + get_submit_action(form)
    submit_data = get_datas(form)
    response = opener.open(submit_to, urllib.urlencode(submit_data))
    
    #TODO 判断登录是否成功
    success_page = response.read()    
    
    #解析gsid
    gsid = parsing_gsid(success_page)
    success = gsid and True or False
    return success, gsid
    

#=== helpers =======
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
    return r and r.group(1) or None

