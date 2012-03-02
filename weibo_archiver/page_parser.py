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


def clear_contents(e):
    """
    helper function, clear the spaces
    """
    _clear = lambda x: x
    _strip = lambda x: x.strip()
    return filter(_clear, map(_strip, e.xpath('.//text()')))


def parse_weibo_page(src):
    """
    #IMPORTANT: 
        如果是当前登录用户自己的微博列表页, 获取到的weibo数恒为10.
        当如何是非当前登录用户的微博列表页, 则存在少于10条微博的可能. 
    手机版微博的结构
    <div class="c" id="M_xxxx">
    </div>

    原创无图片
    <div><span class="ctt">content</span>....<span class="ct">time</span></div>

    原创带图片
    <div><span class="ctt">content</span></div>
    <div><a> <img></a> ... <span class="ct">time</span></div>

    转发无图
    <div><span class="cmt">rt_user</span><span class="ctt">rt_content</span>...</div>
    <div><span class="cmt">...</span>....<span class="ct">time</span></div>

    转发有图
    <div><span class="cmt">...</span></span>
    <div><a><img></a></div>
    <div><span class="cmt">...</span> ... <span class="ct">...</span></div>

    策略. 
    有两个及以上.  先检查图片.  第二个div带img则获取img且移除
    如果只有一个, 必然为原创
    还剩下两个div的话, 必然时转发.
    """
    page = lxml.html.fromstring(src)
    weibos = page.xpath('.//div[starts-with(@id, "M_")]')
    weibo_list = []
    for wb in weibos:
        has_img = False
        src = ""  #因为src没有定义,但又在下面print,导致输出结果出错
        content = ""
        rt_content = ""
        rt_user = ""

        mid = wb.xpath("@id")[0][2:]

        #TODO 对于"几分钟前 ...."的格式没有处理
        time_and_source = wb.xpath('.//span[@class="ct"]//text()')[0].split()
        time = " ".join((time_and_source[0], time_and_source[1]))
        source = time_and_source[2]

        divs = wb.xpath('.//div')
        #先检查图片,有则处理并移除
        if len(divs) > 1:
            xp = divs[1].xpath('.//img/@src')
            if xp:
                src = xp[0]
                has_img = True
                divs.pop(1)
        
        #处理微博内容
        if len(divs) == 1:  #如果只有一个,则为原创
            contents = clear_contents(divs[0])
            content = has_img and " ".join(contents) or " ".join(contents[:-6])
        else:               #否则,则为转发
            contents = clear_contents(divs[1])  #转发理由主体
            content = "".join(contents[1:-6])
            
            #TODO BUG 转发内容删除的情况未处理
            rt_contents = clear_contents(divs[0]) #转发内容主题
            rt_user = rt_contents[1]
            rt_content = "".join(rt_contents[3:-2])
        
        weibo_list.append({
            'mid': mid,
            'content': content,
            'rt_user': rt_user,
            'rt_content': rt_content,
            'img': src,
            'time': time,
            'source': source,
        })
    return weibo_list


if __name__ == "__main__":
    f = open('weibo_page.html', 'r')
    src = f.read()
    f.close()
    weibo_list = parse_weibo_page(src)

