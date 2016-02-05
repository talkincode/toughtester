#!/usr/bin/env python
# coding=utf-8
import os
from toughlib import mcache, storage
from sqlalchemy.sql import text as _sql
from txradius.radius import dictionary
from txradius import client
import functools
import toughtester

class RadiusLoader:

    def __init__(self, config, dbengine):
        self.config = config
        self.dbengine = dbengine
        self.cache = mcache.Mcache()

    def warp(self, result):
        if result:
            radius = storage.Storage()
            radius.ip_addr = result['ip_addr']
            radius.secret = result['secret']
            radius.auth_port = result['auth_port']
            radius.acct_port = result['acct_port']
            radius.dict = dictionary.Dictionary(
                    os.path.join(os.path.dirname(toughtester.__file__),"dictionarys/dictionary"))
            radius.send_auth = functools.partial(
                client.send_auth,
                str(radius.secret),
                radius.dict,
                radius.ip_addr,
                authport=int(radius.auth_port),
                debug=True
            )

            radius.send_acct = functools.partial(
                client.send_acct,
                str(radius.secret),
                radius.dict,
                radius.ip_addr,
                acctport=int(radius.acct_port),
                debug=True
            )
            return radius

    def getRadius(self, host):
        cache_key = 'RadiusLoader.radius.%s' % (host)
        cache = self.cache.get(cache_key)
        if cache:
            return cache
        with self.dbengine.begin() as conn:
            cur = conn.execute(_sql("""select * from tt_radius where ip_addr = :ip_addr """),ip_addr=host)
            radius = self.warp(cur.fetchone())
            self.cache.set(cache_key,radius, expire=60)
            return radius

    def getMasterRadius(self):
        cache_key = 'RadiusLoader.master_radius'
        cache = self.cache.get(cache_key)
        if cache:
            return cache
        with self.dbengine.begin() as conn:
            cur = conn.execute(_sql("select * from tt_radius where serv_type = 1"))
            radius = self.warp(cur.fetchone())
            self.cache.set(cache_key,radius, expire=60)
            return radius

            

