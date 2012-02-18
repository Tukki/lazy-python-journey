#_*_ coding: utf-8 _*_
import logging
import math

import tornado.web
import tornado.ioloop
import tornado.escape

import auth

class AuthenticationHandler(tornado.web.RequestHandler,
                   auth.WeiboOAuthMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(
                self.async_callback(self._on_auth))
            return
        self.authorize_redirect('/login')

    def _on_auth(self, user):
        """
        the OAuth authorized user and access token on callback.
        """
        if not user:
            raise tornado.web.HTTPError(500, "Weibo auth failed")
        cookie = {}
        cookie['access_token'] = user['access_token']
        cookie['username'] = user['username']
        cookie['id'] = user['id']
        self.set_secure_cookie('weibo_session',
                               tornado.escape.json_encode(cookie))
        self.redirect("/")

class HomeHandler(tornado.web.RequestHandler, auth.WeiboOAuthMixin):

    def get_current_user(self):
        session = self.get_secure_cookie('weibo_session')
        if session is None:
            return None
        user = tornado.escape.json_decode(session)
        return user

    def get_login_url(self):
        return "/login"

    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        user = self.get_current_user()
        self.weibo_request('/statuses/unread',
                           access_token=user['access_token'],
                           callback=self.async_callback(self._on_response))
    
    def _on_response(self, data):
        html = []
        html.append('welcome back, %(username)s' % self.get_current_user())
        html.append(str(data))
        self.write("<br>".join(html))
        self.finish()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    settings = {
        "weibo_app_key": "",
        "weibo_app_secret": "",
        'cookie_secret': '',

        'debug': True,
    }

    application = tornado.web.Application([
        (r"/", HomeHandler),
        (r"/login", AuthenticationHandler),
    ], **settings)
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

                   
