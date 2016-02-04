#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
sys.path.insert(0,os.path.split(__file__)[0])
sys.path.insert(0,os.path.abspath(os.path.pardir))
from toughlib import utils
from toughtester import models
from sqlalchemy.orm import scoped_session, sessionmaker
from toughlib.dbengine import get_engine
from hashlib import md5


def init_db(db):

    params = [
        ('system_name',u'管理系统名称',u'ToughWlan管理控制台'),
        ('is_debug',u'DEBUG模式',u'0')
    ]

    for p in params:
        param = models.TTParam()
        param.param_name = p[0]
        param.param_desc = p[1]
        param.param_value = p[2]
        db.add(param)


    opr = models.TTOperator()
    opr.id = 1
    opr.operator_name = u'admin'
    opr.operator_type = 0
    opr.operator_pass = md5('root').hexdigest()
    opr.operator_desc = 'admin'
    opr.operator_status = 0
    db.add(opr)

    radius = models.TTRadius()
    radius.ip_addr = "127.0.0.1"
    radius.name = "local radius"
    radius.secret = "secret"
    radius.acct_port = 1813
    radius.auth_port = 1812
    radius.serv_type = 1
    db.add(radius)

    db.commit()
    db.close()

def update(config):
    print 'starting update database...'
    try:
        db_engine = get_engine(config)
        metadata = models.get_metadata(db_engine)
        metadata.drop_all(db_engine)
        metadata.create_all(db_engine)
        print 'update database done'
        db = scoped_session(sessionmaker(bind=db_engine, autocommit=False, autoflush=True))()
        init_db(db)
    except:
        import traceback
        traceback.print_exc()




        