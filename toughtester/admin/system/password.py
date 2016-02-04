#!/usr/bin/env python
# coding:utf-8
from hashlib import md5
from toughlib import utils
from toughtester.admin.base import BaseHandler, MenuSys
from toughlib.permit import permit
from toughtester import models
from toughtester.admin.system import password_forms


###############################################################################
# password update
###############################################################################
@permit.route(r"/password", u"密码修改", MenuSys, order=1.0100, is_menu=False)
class PasswordUpdateHandler(BaseHandler):
    def get(self):
        form = password_forms.password_update_form()
        form.fill(tra_user=self.get_secure_cookie("tra_user"))
        return self.render("base_form.html", form=form)

    def post(self):
        form = password_forms.password_update_form()
        if not form.validates(source=self.get_params()):
            self.render("base_form.html", form=form)
            return
        if form.d.tra_user_pass != form.d.tra_user_pass_chk:
            self.render("base_form.html", form=form, msg=u'确认密码不一致')
            return
        opr = self.db.query(models.TTOperator).filter_by(operator_name=form.d.tra_user).first()
        opr.operator_pass = md5(form.d.tra_user_pass).hexdigest()

        self.db.commit()
        self.redirect("/")


