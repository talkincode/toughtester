#!/usr/bin/env python
# coding=utf-8
from toughlib import btforms
from toughlib.btforms import rules
from toughlib.btforms.rules import button_style, input_style

opr_status_dict = {0: u'正常', 1: u"停用"}

def operator_add_form():
    return btforms.Form(
        btforms.Textbox("operator_name", rules.len_of(2, 32), description=u"操作员名称", required="required", **input_style),
        btforms.Textbox("operator_desc", rules.len_of(0, 255), description=u"操作员姓名", **input_style),
        btforms.Password("operator_pass", rules.len_of(6, 128), description=u"操作员密码", required="required",**input_style),
        btforms.Dropdown("operator_status", description=u"操作员状态", args=opr_status_dict.items(), required="required",**input_style),
        btforms.Button("submit", type="submit", html=u"<b>提交</b>", **button_style),
        title=u"增加操作员",
        action="/operator/add"
    )


def operator_update_form():
    return btforms.Form(
        btforms.Hidden("id", description=u"编号"),
        btforms.Textbox("operator_name", description=u"操作员名称", readonly="readonly", **input_style),
        btforms.Textbox("operator_desc", rules.len_of(0, 255), description=u"操作员姓名", **input_style),
        btforms.Password("operator_pass", rules.len_of(0, 128), description=u"操作员密码(留空不修改)", autocomplete="off",**input_style),
        btforms.Dropdown("operator_status", description=u"操作员状态", args=opr_status_dict.items(), required="required",**input_style),
        btforms.Button("submit", type="submit", html=u"<b>提交</b>", **button_style),
        title=u"修改操作员",
        action="/operator/update"
    )