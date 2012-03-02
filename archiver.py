#_*_ coding: utf-8 _*_

from weibo_loader import WeiboLoader
from page_parser import parse_weibo_page

def get_args():
    import argparse #获取参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='user email')
    parser.add_argument('-p', '--psw', help="password")
    parser.add_argument('-t', '--target', help='target user ID')
    args = parser.parse_args()

    email = args.user
    psw = args.psw
    target = args.target
    
    return email, psw, target


if __name__ == "__main__":
    email, psw, target = get_args()
    loader = WeiboLoader()
    loader.login(email, psw)
    assert loader.is_logined
    print loader.gsid
    loader.bind_target(target)

    page = loader.load_page(1)
    weibo_list = parse_weibo_page(page)
    for weibo in weibo_list:
        for k, v in weibo.items():
            print k, ": ", v
        print "\n"

