#_*_ coding: utf-8 _*_

from weibo_loader import WeiboLoader

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
