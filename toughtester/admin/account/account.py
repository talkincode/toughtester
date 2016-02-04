#!/usr/bin/env python
# coding:utf-8

import cyclone.web
from toughlib import utils
from toughtester.admin.base import BaseHandler, MenuUser
from toughlib.permit import permit
from toughtester.admin.account import account_form
from toughtester import models

@permit.route(r"/account", u"测试账号管理", MenuUser, order=1.0000, is_menu=True)
class AccountListHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        userlist = self.db.query(models.TTAccount)
        self.render("account_list.html",userlist=userlist)

@permit.route(r"/account/add", u"测试账号新增", MenuUser, order=1.0001)
class AccountAddHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        form = account_form.account_add_form()
        self.render("base_form.html",form=form)

    def post(self):
        form = account_form.account_add_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)

        if self.db.query(models.TTAccount).filter_by(account_number=form.d.account_number).count() > 0:
            return self.render("base_form.html", form=form, msg=u"账号已经存在")

        account = models.TTAccount()
        account.account_number = form.d.account_number
        account.password = form.d.password
        self.db.add(account)
        self.db.commit()
        self.redirect("/account", permanent=False)

@permit.route(r"/account/delete", u"测试账号删除", MenuUser, order=1.0002)
class AccountAddHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        account_number = self.get_argument("account_number")
        self.db.query(models.TTAccount).filter_by(account_number=account_number).delete()
        self.db.commit()
        self.redirect("/account",permanent=False)



@permit.route(r"/account/tester", u"账号测试", MenuUser, order=1.0001, is_menu=True)
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



