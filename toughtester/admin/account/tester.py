#!/usr/bin/env python
# coding:utf-8

import time
import cyclone.web
import cyclone.sse
from toughlib import utils, logger
from toughtester.admin.base import BaseHandler, MenuUser
from toughtester.radius.session import RadiusSession
from toughlib.permit import permit
from toughlib.btforms.rules import is_number
from twisted.internet import defer, reactor
from toughtester import models

def sleep(secs):
    d = defer.Deferred()
    reactor.callLater(secs, d.callback, None)
    return d

@permit.route(r"/account/tester", u"账号测试", MenuUser, order=2.0000, is_menu=True)
class AccountTesterHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        radius_list = self.db.query(models.TTRadius)
        user_list = self.db.query(models.TTAccount).limit(20)
        vendor_list = self.db.query(models.TTVendor)
        self.render("account_tester.html",
            radius_list=radius_list,
            vendor_list=vendor_list,
            user_list=user_list,**self.get_params())



@permit.route(r"/account/tester/auth", u"认证消息测试", MenuUser, order=2.0001)
class AuthTesterHandler(BaseHandler):

    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def post(self):
        account_number = self.get_argument("account_number",None)
        radius_ipaddr = self.get_argument("radius_ipaddr",None)
        vendor_id = self.get_argument("vendor_id",None)
        password = self.db.query(models.TTAccount).get(account_number).password
        rad_session = RadiusSession(self.settings.config,self.settings.db_engine,radius_ipaddr=radius_ipaddr)
        resp = yield rad_session.start(account_number,password)
        self.render_json(**resp)

class PressTestMixin(object):
    mbuffer = ""
    waiters = []

    def subscribe(self, client):
        PressTestMixin.waiters.append(client)

    def unsubscribe(self, client):
        PressTestMixin.waiters.remove(client)

    def broadcast(self, message):
        cls = PressTestMixin
        for client in cls.waiters:
            try:
                client.sendEvent(message)
            except Exception as e:
                logger.exception(e)

class StatCounter:

    def __init__(self):
        self.starttime = time.time()
        self.requests = 0
        self.replys = 0
        self.lasttime = self.starttime  
        self.stat_time = time.time()

    def plus(self):
        self.replys += 1
        self.lasttime = time.time()
        if self.lasttime - self.stat_time > 2:
            result = []
            _sectimes = self.lasttime - self.starttime
            _percount = self.replys /(_sectimes < 0 and 0 or _sectimes)
            result.append("Current sender %s request"% self.requests)
            result.append("Current received %s response"% self.replys)
            result.append("response per second:%s"%_percount)
            self.stat_time = self.lasttime
            return result



@permit.route(r"/account/tester/press", u"压力测试", MenuUser, order=2.0001)
class PressTesterHandler(BaseHandler,PressTestMixin):

    def on_stat(self,resp):
        if resp.get('code') == 0:
            result = self.stat_counter.plus()
            if result:
                self.broadcast("<br><br>".join(result)) 


    @defer.inlineCallbacks
    @cyclone.web.authenticated
    def post(self):
        account_number = self.get_argument("account_number",None)
        radius_ipaddr = self.get_argument("radius_ipaddr",None)
        vendor_id = self.get_argument("vendor_id",None)
        test_times = self.get_argument("test_times",0)
        if not is_number.valid(test_times):
            self.broadcast("test_times not valid")
            return
        password = self.db.query(models.TTAccount).get(account_number).password
        self.stat_counter = StatCounter()
        for i in range(int(test_times)):
            rad_session = RadiusSession(self.settings.config,
                self.settings.db_engine,
                radius_ipaddr=radius_ipaddr)
            d = rad_session.start(account_number,password)
            self.stat_counter.requests += 1
            d.addCallbacks(self.on_stat,logger.error)
            yield sleep(0.01)

        self.render_json(code=0,msg=u"done")
            

@permit.route(r"/account/tester/sse", u"测试消息", MenuUser, order=2.0002)
class PressTestHandler(cyclone.sse.SSEHandler, PressTestMixin):
    def bind(self):
        self.subscribe(self)

    def unbind(self):
        self.unsubscribe(self)

