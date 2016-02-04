#!/usr/bin/env python
# coding=utf-8
from toughlib import btforms
from toughlib.btforms import rules
from toughlib.btforms.rules import button_style, input_style

account_add_form = btforms.Form(
    btforms.Textbox("account_number", rules.len_of(1, 32), description=u"账号", required="required", **input_style),
    btforms.Textbox("password", rules.len_of(1, 32), description=u"密码", required="required", **input_style),
    btforms.Button("submit", type="submit", html=u"<b>提交</b>", **button_style),
    title=u"新增测试账号",
    action="/account/add"
)


