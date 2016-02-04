#!/usr/bin/env python
#coding:utf-8
from hashlib import md5
from toughlib import utils
from toughtester.admin.base import BaseHandler
from toughtester import models
from toughlib.permit import permit

@permit.route(r"/login")
class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        uname = self.get_argument("username")
        upass = self.get_argument("password")
        if not uname:
            return self.render_json(code=1, msg=u"请填写用户名")
        if not upass:
            return self.render_json(code=1, msg=u"请填写密码")

        enpasswd = md5(upass.encode()).hexdigest()

        opr = self.db.query(models.TTOperator).filter_by(
            operator_name=uname,
            operator_pass=enpasswd
        ).first()
        if not opr:
            return self.render_json(code=1, msg=u"用户名密码不符")

        if opr.operator_status == 1:
            return self.render_json(code=1, msg=u"该操作员账号已被停用")

        self.set_session_user(uname, self.request.remote_ip, opr.operator_type, utils.get_currtime())

        if opr.operator_type == 1:
            for rule in self.db.query(models.TTOperatorRule).filter_by(operator_name=uname):
                permit.bind_opr(rule.operator_name, rule.rule_path)

        self.db.commit()

        self.render_json(code=0, msg="ok")

