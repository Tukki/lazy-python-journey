#_*_ coding: utf-8 _*_

import tornado.ioloop
import tornado.web

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('home.html')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        uid = self.get_argument('uid')
        assert uid
        self.render('main.html', 
                    uid=uid,
                    source=365315726,
                   )


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", HomeHandler),
        (r'/u', MainHandler),
    ], debug=True)
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

