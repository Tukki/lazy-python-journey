#_*_ coding: utf-8 _*_
from __future__ import division, with_statement

import logging
import urllib

from tornado import httpclient
from tornado import escape
from tornado.auth import OAuthMixin

class WeiboOAuthMixin(OAuthMixin):
    _OAUTH_REQUEST_TOKEN_URL = "http://api.t.sina.com.cn/oauth/request_token"
    _OAUTH_ACCESS_TOKEN_URL = "http://api.t.sina.com.cn/oauth/access_token"
    _OAUTH_AUTHORIZE_URL = "http://api.t.sina.com.cn/oauth/authorize"
    _OAUTH_NO_CALLBACKS = False 
    _OAUTH_VERSION = "1.0a"

    def weibo_request(self, path, callback, access_token=None, post_args=None, **args):
        if path.startswith('http:') or path.startswith('https:'):
            url = path
        else:
            url = "http://api.t.sina.com.cn" + path + ".json"
        #add the OAuth resource request signature if we have credentials
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            args.update(oauth)
        if args:
            url += "?" + urllib.urlencode(args)
        callback = self.async_callback(self._on_weibo_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_weibo_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))
    
    def _oauth_consumer_token(self):
        self.require_setting("weibo_app_key", "Weibo OAuth")
        self.require_setting("weibo_app_secret", "Weibo Oauth")
        return dict(
            key=self.settings["weibo_app_key"],
            secret=self.settings["weibo_app_secret"])

    def _oauth_get_user(self, access_token, callback):
        logging.debug('oauth get user access_token: %s', access_token)
        """
        the access token includes secret, key, user_id
        """
        callback = self.async_callback(self._parse_user_response, callback)
        self.weibo_request(
            "/users/show/" + access_token["user_id"],
            access_token=access_token,
            callback=callback)

    def _parse_user_response(self, callback, user):
        # It just work like TwitterMixin, but I don't known if this  user['username'] is matter to tornado
        if user:
            user["username"] = user["screen_name"]
        callback(user)

