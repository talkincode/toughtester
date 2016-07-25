#!/usr/bin/env python
#coding:utf-8
import sys
import os
import time
import cyclone.web
from twisted.python import log
from twisted.internet import reactor
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from mako.lookup import TemplateLookup
from sqlalchemy.orm import scoped_session, sessionmaker
from toughlib import utils
from toughlib import logger
from toughtester import models
from toughlib.dbengine import get_engine
from toughlib.permit import permit, load_handlers
from toughlib import db_session as session
from toughlib import db_cache as cache
from toughlib.db_backup import DBBackup
import toughtester



class Httpd(cyclone.web.Application):
    def __init__(self, config=None, dbengine=None, **kwargs):

        self.config = config
        self.db_engine = dbengine

        settings = dict(
            cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            template_path=os.path.join(os.path.dirname(toughtester.__file__), "views"),
            static_path=os.path.join(os.path.dirname(toughtester.__file__), "static"),
            xsrf_cookies=True,
            config=self.config,
            db_engine=self.db_engine,
            debug=self.config.system.debug,
            xheaders=True,
        )

        self.cache = CacheManager(**parse_cache_config_options({
            'cache.type': 'file',
            'cache.data_dir': '/tmp/cache/data',
            'cache.lock_dir': '/tmp/cache/lock'
        }))

        self.tp_lookup = TemplateLookup(directories=[settings['template_path']],
                                        default_filters=['decode.utf8'],
                                        input_encoding='utf-8',
                                        output_encoding='utf-8',
                                        encoding_errors='replace',
                                        module_directory="/tmp")

        self.db = scoped_session(sessionmaker(bind=self.db_engine, autocommit=False, autoflush=False))
        self.session_manager = session.SessionManager(settings["cookie_secret"], self.db_engine, 86400)
        self.mcache = cache.CacheManager(self.db_engine)
        self.db_backup = DBBackup(models.get_metadata(self.db_engine), excludes=['system_session','system_cache'])

        permit.add_route(cyclone.web.StaticFileHandler,
                         r"/backup/download/(.*)",
                         u"下载数据",
                         u"系统管理",
                         handle_params={"path": self.config.database.backup_path},
                         order=1.0405)

        self.init_route()
        cyclone.web.Application.__init__(self, permit.all_handlers, **settings)

    def init_route(self):
        handler_path = os.path.join(os.path.abspath(os.path.dirname(toughtester.__file__)), "admin")
        load_handlers(handler_path=handler_path, pkg_prefix="toughtester.admin",excludes=['views','httpd','ddns_task'])

        conn = self.db()
        oprs = conn.query(models.TTOperator)
        for opr in oprs:
            if opr.operator_type > 0:
                for rule in self.db.query(models.TTOperatorRule).filter_by(operator_name=opr.operator_name):
                    permit.bind_opr(rule.operator_name, rule.rule_path)
            elif opr.operator_type == 0:  # 超级管理员授权所有
                permit.bind_super(opr.operator_name)


def run(config, dbengine=None):
    app = Httpd(config, dbengine=dbengine)
    reactor.listenTCP(config.admin.port, app, interface=config.admin.host)

