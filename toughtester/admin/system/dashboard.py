#!/usr/bin/env python
# coding:utf-8
import os
import subprocess
import os.path
import cyclone.web
from toughtester.admin.base import BaseHandler, MenuSys
from toughlib.permit import permit


@permit.route(r"/")
class HomeHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.redirect("/dashboard",permanent=False)


@permit.route(r"/dashboard", u"控制面板", MenuSys, order=1.0000, is_menu=True, is_open=False)
class DashboardHandler(BaseHandler):

    @cyclone.web.authenticated
    def get(self):
        self.render("index.html", config=self.settings.config)




