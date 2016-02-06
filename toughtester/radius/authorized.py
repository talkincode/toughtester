#!/usr/bin/env python
# coding=utf-8
import os
import six
from twisted.internet import protocol, reactor
from txradius import message
from toughlib import logger,dispatch
from txradius.radius import dictionary
from txradius.radius import packet
from toughtester.radius.session import RadiusSession
from toughtester.radius.radius_loader import RadiusLoader
import toughtester

class RadiusdAuthorize(protocol.DatagramProtocol):
    def __init__(self, config, dbengine=None):
        self.config = config
        self.dbengine = dbengine
        self.radloader = RadiusLoader(config,dbengine)

    def processPacket(self, coareq, (host,port)):
        session_id = coareq.get_acct_sessionid()
        session = RadiusSession.sessions.pop(session_id,None)
        if session:
            session.stop()
        reply = coareq.CreateReply()
        logger.info("[RADIUSAuthorize] :: Send Authorize radius response: %s" % (repr(reply)))
        if self.config.radius.debug:
            logger.debug(message.format_packet_str(reply))
        self.transport.write(reply.ReplyPacket(),  (host, port))


    def datagramReceived(self, datagram, (host, port)):
        try:
            radius = self.radloader.getRadius(host)
            if not radius:
                logger.info('[RADIUSAuthorize] :: Dropping Authorize packet from unknown host ' + host)
                return

            coa_req = message.CoAMessage(packet=datagram, dict=radius.dict, secret=six.b(radius.secret))
            logger.info("[RADIUSAuthorize] :: Received Authorize radius request: %s" % message.format_packet_log(coa_req))

            if self.config.radius.debug:
                logger.debug(message.format_packet_str(coa_req))

            self.processPacket(coa_req,  (host, port))

        except packet.PacketError as err:
            errstr = 'RadiusError:Dropping invalid packet from {0} {1},{2}'.format(
                host, port, utils.safeunicode(err))
            logger.error(errstr)


def run(config, dbengine=None):
    authorize_protocol = RadiusdAuthorize(config, dbengine=dbengine)
    reactor.listenUDP(int(config.radius.authorize_port), authorize_protocol, interface=config.radius.host)





