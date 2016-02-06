#!/usr/bin/env python
# coding:utf-8

import cyclone.web
from toughlib import utils
from toughtester.admin.base import BaseHandler, MenuUser
from toughlib.permit import permit
from twisted.internet import defer
from toughtester.radius.session import RadiusSession
from toughtester import models

def fmt_time(times):
    d = times / (3600 * 24)
    h = times % (3600 * 24) / 3600
    m = times % (3600 * 24) % 3600 / 60

    if int(d) > 0:
        return u"%s天%s小时%s分钟" % (int(d), int(h), int(m))
    elif int(d) > 0 and int(h) > 0:
        return u"%s小时%s分钟" % (int(h), int(m))
    else:
        return u"%s分钟" % (int(m))

@permit.route(r"/account/session", u"在线会话管理", MenuUser, order=3.0000, is_menu=True)
class AccountSessionHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.render("account_sessions.html",session_list = RadiusSession.sessions,fmt_time=fmt_time)


@permit.route(r"/account/session/stop", u"在线会话解锁", MenuUser, order=3.0001)
class AccountSessionStopHandler(BaseHandler):
    @cyclone.web.authenticated
    def post(self):
        session_id = self.get_argument("session_id")
        RadiusSession.stop_session(session_id=session_id)
        self.render_json(code=0,msg=u"stop session done")
