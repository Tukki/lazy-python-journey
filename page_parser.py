#_*_ coding: utf-8 _*_
import re
import lxml.html

def parse_login_form(page_src):
    """
    parse login form infos from the login page src
    return the form action and the values list
    """
    page = lxml.html.fromstring(page_src)
    form = page.forms[0]
    return form.action, form.form_values()


def update_form_values(values, email, psw):
    """
    update form values with email and psw
    """
    def _updater(value):
        if value[0] == 'mobile':
            return value[0], email
        elif value[0].startswith('password'):
            return value[0], psw
        else:
            return value[0], value[1].encode('utf8')
    values = map(_updater, values)
    values.append(('submit', '登录'))   #need this, otherwise, login failed
    return values


def parse_gsid(success_page):
    """
    parse the gsid from the success login page
    """
    r = re.search(r'gsid=(\w+)&amp;', success_page)
    return r and r.group(1) or None


