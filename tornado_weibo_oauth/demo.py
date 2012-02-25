#_*_ coding: utf-8 _*_
import logging
import math

import tornado.web
import tornado.ioloop
import tornado.escape

import tornado_weibo_oauth

class AuthenticationHandler(tornado.web.RequestHandler,
                   tornado_weibo_oauth.WeiboOAuthMixin):
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
        logging.debug(user)
        #do some with the user or the access_token 
        self.set_secure_cookie('weibo_session',
                               tornado.escape.json_encode(user))
        self.redirect("/")

class BaseHandler(tornado.web.RequestHandler, tornado_weibo_oauth.WeiboOAuthMixin):

    def get_current_user(self):
        session = self.get_secure_cookie('weibo_session')
        if session is None:
            return None
        user = tornado.escape.json_decode(session)
        return user

    def get_login_url(self):
        return "/login"


class HomeHandler(BaseHandler):
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


from tornado import gen
from tornado import httpclient

class GenAsyncHandler(BaseHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        user = self.get_current_user()
        r1, r2 = yield [gen.Task(self.weibo_request, 
                                 '/statuses/unread', 
                                 access_token=user['access_token']),
                        gen.Task(self.weibo_request,
                                 '/statuses/user_timeline',
                                 access_token=user['access_token']),
                       ]
        self.write(r1)
        self.write(str(r2))
        self.finish()  #must finish


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
        (r'/gen', GenAsyncHandler),
    ], **settings)
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

                   
