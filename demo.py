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
        if not user:
            raise tornado.web.HTTPError(500, "Weibo auth failed")
        self.set_secure_cookie('weibo_session',
                               tornado.escape.json_encode(user),
                               #math.ceil(user['session_expires'] / 86400.0)
                              )
        self.redirect("/")
        #self.write(user)

class HomeHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        session = self.get_secure_cookie('weibo_session')
        if session is None:
            return None
        user = tornado.escape.json_decode(session)
        return user

    def get_login_url(self):
        return "/login"

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        self.write(user)

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

                   
