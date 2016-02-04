#!/usr/bin/env python
#coding:utf-8
import json
import re
import urlparse
import urllib
import traceback
import cyclone.web
from cyclone.util import ObjectDict
from toughlib import utils,dispatch,logger
from toughlib.permit import permit
from toughlib.paginator import Paginator
from toughlib import db_session as session
from toughtester import __version__ as sys_version
from toughtester import models


ADMIN_MENUS = (MenuSys, MenuRes, MenuUser) = (u"系统管理", u"资源管理", u"用户管理")

MENU_ICONS = {
    u"系统管理": "fa fa-cog",
    u"资源管理": "fa fa-desktop",
    u"用户管理": "fa fa-users"
}


class BaseHandler(cyclone.web.RequestHandler):
    
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.cache = self.application.mcache
        self.session = session.Session(self.application.session_manager, self)
        self.db_backup = self.application.db_backup


    def initialize(self):
        self.tp_lookup = self.application.tp_lookup
        self.db = self.application.db()
        
    def on_finish(self):
        self.db.close()
        
    def get_error_html(self, status_code=500, **kwargs):
        try:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return self.render_json(code=1, msg=u"%s:服务器处理失败，请联系管理员" % status_code)

            if status_code == 404:
                return self.render_string("error.html", msg=u"404:页面不存在")
            elif status_code == 403:
                return self.render_string("error.html", msg=u"403:非法的请求")
            elif status_code == 500:
                logger.info(traceback.format_exc())
                return self.render_string("error.html", msg=u"500:服务器处理失败，请联系管理员")
            else:
                return self.render_string("error.html", msg=u"%s:服务器处理失败，请联系管理员" % status_code)
        except:
             return self.render_string("error.html", msg=u"%s:服务器处理失败，请联系管理员" % status_code)

    def render(self, template_name, **template_vars):
        html = self.render_string(template_name, **template_vars)
        self.write(html)

    def render_error(self, **template_vars):
        tpl = "error.html"
        html = self.render_string(tpl, **template_vars)
        self.write(html)

    def render_json(self, **template_vars):
        if not template_vars.has_key("code"):
            template_vars["code"] = 0
        resp = json.dumps(template_vars, ensure_ascii=False)
        if self.settings.debug:
            logger.debug("[api debug] :: %s response body: %s" % (self.request.path, utils.safestr(resp)))
        self.write(resp)


    def render_string(self, template_name, **template_vars):
        template_vars["xsrf_form_html"] = self.xsrf_form_html
        template_vars["current_user"] = self.current_user
        template_vars["login_time"] = self.get_secure_cookie("portal_logintime")
        template_vars["request"] = self.request
        template_vars["handler"] = self
        template_vars["utils"] = utils
        template_vars['sys_version'] = sys_version
        template_vars["permit"] = permit
        template_vars["menu_icons"] = MENU_ICONS
        template_vars["all_menus"] = permit.build_menus(
            order_cats=ADMIN_MENUS
        )
        mytemplate = self.tp_lookup.get_template("admin/{0}".format(template_name))
        return mytemplate.render(**template_vars)


    def render_from_string(self, template_string, **template_vars):
        from mako.template import Template
        template = Template(template_string)
        return template.render(**template_vars)


    def get_page_data(self, query):
        page_size = self.application.settings.get("page_size",15)
        page = int(self.get_argument("page", 1))
        offset = (page - 1) * page_size
        result = query.limit(page_size).offset(offset)
        page_data = Paginator(self.get_page_url, page, query.count(), page_size)
        page_data.result = result
        return page_data
   

    def get_page_url(self, page, form_id=None):
        if form_id:
            return "javascript:goto_page('%s',%s);" %(form_id.strip(),page)
        path = self.request.path
        query = self.request.query
        qdict = urlparse.parse_qs(query)
        for k, v in qdict.items():
            if isinstance(v, list):
                qdict[k] = v and v[0] or ''

        qdict['page'] = page
        return path + '?' + urllib.urlencode(qdict)
        
    def set_session_user(self, username, ipaddr, opr_type, login_time):
        session_opr = ObjectDict()
        session_opr.username = username
        session_opr.ipaddr = ipaddr
        session_opr.opr_type = opr_type
        session_opr.login_time = login_time
        self.session['session_opr'] = session_opr
        self.session.save()

    def clear_session(self):
        self.session.clear()
        self.session.save()
        self.clear_all_cookies()  
        
    def get_current_user(self):
        return self.session.get("session_opr")

    def get_params(self):
        arguments = self.request.arguments
        params = {}
        for k, v in arguments.items():
            if len(v) == 1:
                params[k] = v[0]
            else:
                params[k] = v
        return params

    def get_params_obj(self, obj):
        arguments = self.request.arguments
        for k, v in arguments.items():
            if len(v) == 1:
                if type(v[0]) == str:
                    setattr(obj, k, v[0].decode('utf-8', ''))
                else:
                    setattr(obj, k, v[0])
            else:
                if type(v) == str:
                    setattr(obj, k, v.decode('utf-8'))
                else:
                    setattr(obj, k, v)
        return obj





