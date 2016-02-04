#!/usr/bin/env python
#coding:utf-8
import warnings
import sqlalchemy
warnings.simplefilter('ignore', sqlalchemy.exc.SAWarning)
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


def get_metadata(db_engine):
    global DeclarativeBase
    metadata = DeclarativeBase.metadata
    metadata.bind = db_engine
    return metadata


class SystemSession(DeclarativeBase):
    """session表"""
    __tablename__ = 'system_session'

    __table_args__ = {
        'mysql_engine' : 'MEMORY'
    }

    key = Column(u'_key', Unicode(length=512), primary_key=True, nullable=False,doc=u"session key")
    value = Column(u'_value', Unicode(length=2048), nullable=False,doc=u"session value")
    time = Column(u'_time', INTEGER(), nullable=False,doc=u"session timeout")

class SystemCache(DeclarativeBase):
    """cache表"""
    __tablename__ = 'system_cache'

    __table_args__ = {
        'mysql_engine' : 'MEMORY'
    }

    key = Column(u'_key', Unicode(length=512), primary_key=True, nullable=False,doc=u"cache key")
    value = Column(u'_value', Unicode(length=4096), nullable=False,doc=u"cache value")
    time = Column(u'_time', INTEGER(), nullable=False,doc=u"cache timeout")



class TTOperator(DeclarativeBase):
    """操作员表 操作员类型 0 系统管理员 1 普通操作员"""
    __tablename__ = 'tt_operator'

    __table_args__ = {}

    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False,doc=u"操作员id")
    operator_type = Column('operator_type', INTEGER(), nullable=False,doc=u"操作员类型")
    operator_name = Column(u'operator_name', Unicode(32), nullable=False,doc=u"操作员名称")
    operator_pass = Column(u'operator_pass', Unicode(length=128), nullable=False,doc=u"操作员密码")
    operator_status = Column(u'operator_status', INTEGER(), nullable=False,doc=u"操作员状态,0/1")
    operator_desc = Column(u'operator_desc', Unicode(255), nullable=False,doc=u"操作员描述")

class TTOperatorRule(DeclarativeBase):
    """操作员权限表"""
    __tablename__ = 'tt_operator_rule'

    __table_args__ = {}
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False,doc=u"权限id")
    operator_name = Column(u'operator_name', Unicode(32), nullable=False,doc=u"操作员名称")
    rule_path = Column(u'rule_path', Unicode(128), nullable=False,doc=u"权限URL")
    rule_name = Column(u'rule_name', Unicode(128), nullable=False,doc=u"权限名称")
    rule_category = Column(u'rule_category', Unicode(128), nullable=False,doc=u"权限分类")


class TTParam(DeclarativeBase):
    """系统参数表  """
    __tablename__ = 'tt_param'

    __table_args__ = {}

    #column definitions
    param_name = Column(u'param_name', Unicode(length=64), primary_key=True, nullable=False,doc=u"参数名")
    param_value = Column(u'param_value', Unicode(length=1024), nullable=False,doc=u"参数值")
    param_desc = Column(u'param_desc', Unicode(length=255),doc=u"参数描述")


class TTVendor(DeclarativeBase):
    """Vendor表 """
    __tablename__ = 'tt_vendor'

    __table_args__ = {}

    #column definitions
    vendor_id = Column('vendor_id', Unicode(length=16),primary_key=True,nullable=False)
    vendor_desc = Column(u'vendor_desc', Unicode(length=64), nullable=False, doc=u"vendor描述")

class TTVendorAttr(DeclarativeBase):
    """Vendor属性 """
    __tablename__ = 'tt_vendor_attr'

    __table_args__ = {}

    # column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False, doc=u"属性id")
    vendor_id = Column('vendor_id', Unicode(length=16),nullable=False)
    attr_name = Column(u'attr_name', Unicode(length=128), nullable=False, doc=u"属性名")
    attr_value = Column(u'attr_value', Unicode(length=255), nullable=False, doc=u"属性值")
    attr_desc = Column(u'attr_desc', Unicode(length=255), doc=u"属性描述")
    UniqueConstraint('vendor_id',"attr_name", name='unique_vendor_attr')


class TTRadius(DeclarativeBase):
    """radius节点表 """
    __tablename__ = 'tt_radius'

    __table_args__ = {}

    # column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False, doc=u"id")
    ip_addr = Column(u'ip_addr', Unicode(length=15), nullable=False, doc=u"IP地址")
    serv_type = Column(u'serv_type', INTEGER(),doc=u"Radius服务器类型，1:master/0:slave")
    name = Column(u'name', Unicode(length=64), nullable=False, doc=u"radius名称")
    secret = Column(u'secret', Unicode(length=64), nullable=False, doc=u"共享密钥")
    auth_port = Column(u'auth_port', INTEGER(), nullable=False, doc=u"认证端口")
    acct_port = Column(u'acct_port', INTEGER(), nullable=False, doc=u"记账端口")


class TTAccount(DeclarativeBase):
    """
    上网账号表
   
    """

    __tablename__ = 'tt_account'

    __table_args__ = {}

    account_number = Column('account_number', Unicode(length=32),primary_key=True,nullable=False,doc=u"上网账号")
    password = Column('password', Unicode(length=128), nullable=False,doc=u"上网密码")


