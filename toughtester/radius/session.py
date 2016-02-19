#!/usr/bin/env python
# coding=utf-8
import uuid
import time
import random
from IPy import IP
from txradius.radius import packet
from twisted.internet import defer
from twisted.internet import task
from twisted.python import log
from twisted.internet import reactor
from txradius import message
from toughlib import dispatch, logger
from toughtester.radius.radius_loader import RadiusLoader

class RadiusSession:

    iplist = (ip for ip in IP('10.0.0.0/16'))
    sessions = {}

    def __init__(self, config, dbengine,radius_ipaddr=None):
        self.config = config
        self.running = False
        self.radius_ipaddr = radius_ipaddr
        self.radloader = RadiusLoader(self.config,dbengine)
        self.session_start = int(time.time())
        self.session_id = uuid.uuid1().hex.upper()
        self.session_data = {}
        self.interim_update = self.config.radius.interim_update

    @property
    def radius(self):
        radius = None
        if self.radius_ipaddr:
            radius = self.radloader.getRadius(self.radius_ipaddr)
        return radius or self.radloader.getMasterRadius()

    @property
    def next_ip(self):
        return next(RadiusSession.iplist).strNormal()

    @property
    def random_mac(self):
        mac = [ 0x52, 0x54, 0x00,
                random.randint(0x00, 0x7f),
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))



    @staticmethod
    def stop_session(ipaddr=None,session_id=None):
        if session_id:
            session = RadiusSession.sessions.pop(session_id,None)
            if session:
                session.stop()
        elif ipaddr:
            ids = []
            for session in RadiusSession.sessions.values():
                if session.session_data['Framed-IP-Address'] == ipaddr:
                    ids.append(session.session_id)
            for sid in ids:
                session = RadiusSession.sessions.pop(sid)
                session.stop()


    @defer.inlineCallbacks
    def start(self, username, password, challenge=None, chap_pwd=None, **kwargs):
        loginfo = []
        auth_req = {'User-Name' : username}
        auth_req["NAS-IP-Address"]     =  kwargs.pop("NAS-IP-Address",self.config.radius.nasaddr)
        auth_req["NAS-Port"]           =  kwargs.pop("NAS-Port",0)
        auth_req["Service-Type"]       =  kwargs.pop("Service-Type","Login-User")
        auth_req["NAS-Identifier"]     =  kwargs.pop("NAS-Identifier",self.config.radius.nasid)
        auth_req["Called-Station-Id"]  =  kwargs.pop("Called-Station-Id",self.random_mac)
        auth_req["Framed-IP-Address"]  =  kwargs.pop("Framed-IP-Address",self.next_ip)
        auth_req.update(kwargs)
        auth_resp = {}
        if challenge and chap_pwd:
            auth_req['CHAP-Challenge'] = challenge
            auth_req['CHAP-Password'] = chap_pwd
            loginfo.append(repr(auth_req))
            auth_resp = yield self.radius.send_auth(**auth_req)
        else:
            auth_req['User-Password'] = password
            loginfo.append(repr(auth_req))
            auth_resp = yield self.radius.send_auth(**auth_req)

        loginfo.append(message.format_packet_log(auth_resp))

        if auth_resp.code== packet.AccessReject:
            defer.returnValue(dict(code=1, 
                msg=auth_resp.get("Reply-Message", "auth reject"),
                loginfo='<br><br>'.join(loginfo)))

        if auth_resp.code== packet.AccessAccept:
            self.session_data['User-Name'] = username
            self.session_data['Acct-Session-Time'] = 0
            self.session_data['Acct-Status-Type'] = 1
            self.session_data['Session-Timeout'] = message.get_session_timeout(auth_resp)
            self.session_data['Acct-Session-Id'] = self.session_id
            self.session_data["NAS-IP-Address"]     = kwargs.pop("NAS-IP-Address",self.config.radius.nasaddr)
            self.session_data["NAS-Port"]           = kwargs.pop("NAS-Port",0)
            self.session_data["NAS-Identifier"]     = kwargs.pop("NAS-Identifier",self.config.radius.nasid)
            self.session_data["Called-Station-Id"]  = kwargs.pop("Called-Station-Id",self.random_mac)
            self.session_data["Framed-IP-Address"]  = kwargs.pop("Framed-IP-Address",self.next_ip)
            self.session_data["Acct-Output-Octets"]  =  0
            self.session_data["Acct-Input-Octets"]  =  0
            self.session_data["NAS-Port-Id"]  =  kwargs.pop("NAS-Port-Id","3/0/1:0.0")
            self.session_data.update(kwargs)
            if 'Acct-Interim-Interval' in auth_resp:
                self.interim_update = message.get_interim_update(auth_resp)

            loginfo.append(repr(self.session_data))
            acct_resp = yield self.radius.send_acct(**self.session_data)
            loginfo.append(message.format_packet_log(acct_resp))
            if acct_resp.code == packet.AccountingResponse:
                self.running = True
                logger.info('Start session  %s' % self.session_id)
                RadiusSession.sessions[self.session_id] = self
                reactor.callLater(self.interim_update,self.check_session)
                defer.returnValue(dict(code=0,msg=u"success",loginfo='<br><br>'.join(loginfo)))
            else:
                defer.returnValue(dict(code=1,msg=u"error",loginfo='<br><br>'.join(loginfo)))

    @defer.inlineCallbacks
    def update(self):
        logger.info('Alive session  %s' % self.session_id)
        self.session_data['Acct-Status-Type'] = 3
        self.session_data["Acct-Output-Octets"]  +=  random.randint(102400, 81920000)
        self.session_data["Acct-Input-Octets"]  +=  random.randint(10240, 819200)
        self.session_data['Acct-Session-Time'] = (int(time.time()) - self.session_start)
        acct_resp = yield self.radius.send_acct(**self.session_data)
        defer.returnValue(acct_resp)

    @defer.inlineCallbacks
    def stop(self):
        self.running = False
        logger.info('Stop session  %s' % self.session_id)
        self.session_data['Acct-Status-Type'] = 2
        self.session_data["Acct-Output-Octets"]  +=  random.randint(102400, 81920000)
        self.session_data["Acct-Input-Octets"]  +=  random.randint(10240, 819200)
        self.session_data['Acct-Session-Time'] = (int(time.time()) - self.session_start)
        acct_resp = yield self.radius.send_acct(**self.session_data)
        defer.returnValue(acct_resp)

    def check_session(self):
        session_time = int(time.time()) - self.session_start
        if session_time > self.session_data['Session-Timeout']:
            self.stop().addCallbacks(logger.info,logger.error)
        else:
            if not self.running:
                return
            self.update().addCallbacks(logger.info,logger.error)
            reactor.callLater(self.interim_update,self.check_session)

























