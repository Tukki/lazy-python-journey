#_*_ coding: utf-8 _*_

import re

#TODO test
def get_mids(page_source):
    """
    获取页面上面带有的微博mids
    期望格式:
        <div class="c" id="M_xwekjWLEj">xx</div>
        <div class="c" id="M_xwdfateat">oo</div>
        ....
    """
    mids = re.findall(r"<div.*id=\"M_(\w+)\".*>", page_source)
    return mids


def get_weibo(soup, mid):
    """
    根据目标id获取对应的微博Soup
    """
    id = "M_%s" % mid
    return soup.find(id=id)
    

def get_page_info(soup):
    """
    获取页面信息.
    避免微博信息中带 "\d+/\+d" 模式,只对分页部分进行处理
    返回(当前页,总页数)
    期望:
        <div id="pagelist">...1/100页</div>
    """
    text = soup.find(id='pagelist').text
    result = re.search(r"(\d+)/(\d+)", text)
    return int(result.group(1)), int(result.group(2))


def get_weibo_count(page):
    pt = r'微博\[(\d+)\]'
    result = re.findall(pt, page)
    assert len(result) == 1
    return int(result[0])


def _is_retweet(wb):
    """
    至今没在原创的微博内容里面看到span.cmt
    """
    return bool(wb.find('span', 'cmt'))

def _get_text(wb, is_retweet):
    if is_retweet:
        #获取"转发理由"
        text = wb.findAll('div')[-1].text
        text = text[5:text.rfind(u'&nbsp;转发[')]
    else:
        text = wb.find('span', 'ctt').text
    return text


def _get_retweet(wb):
    """
    当是retweet的时候,span.ctt为转发的内容
    """
    return wb.find('span', 'ctt').text

def _get_rtuser(wb):
    #"转发了&nsbp;@XXOO&nbsp;的微博"
    #需要考虑转发的目标已被删除
    cmt = wb.find('span', 'cmt')
    user_link = cmt.find('a')
    if user_link:
        text = user_link.text
    else:
        text = cmt.text
    return text

def _get_image(wb):
    """
        <img src="sssscccx" class="ib" />
    """
    img = wb.find('img', 'ib')
    if img:
        src = img.attrMap['src']
        name = src[src.rfind('/')+1:]
    else:
        name = ""
    return name

def _get_time(wb):
    return wb.find('span', 'ct').text.split('&nbsp;')[0]

def _get_source(wb):
    return wb.find('span', 'ct').text.split('&nbsp;')[1]

def parse_weibo(soup, mid):
    wb = get_weibo(soup, mid)
    is_retweet = _is_retweet(wb)
    content = _get_text(wb, is_retweet)
    image = _get_image(wb)
    rt_user = is_retweet and _get_rtuser(wb) or ""
    rt_content = is_retweet and _get_retweet(wb) or ""
    time = _get_time(wb)
    source = _get_source(wb)

    return {
        'mid': mid, 
        'text': content,
        'image': image,
        'time': time,
        'source': source,
        'is_retweet': is_retweet,
        'rt_user': rt_user,
        'rt_text': rt_content,
    }

    

"""
    TODO 
    时间解析
    20分组前
    今天 17:56
    12月23日 09:29
    2009-09-26 14:42:05 
"""

