#!/usr/bin/env python
# coding=utf-8
from toughlib import btforms
from toughlib.btforms import rules
from toughlib.btforms.rules import button_style, input_style


def vendor_add_vform():
    return btforms.Form(
        btforms.Textbox("vendor_id", rules.is_alphanum2(1,16), description=u"模板ID",required="required", **input_style),
        btforms.Textbox("vendor_desc", rules.not_null, description=u"模板描述",required="required", **input_style),
        btforms.Button("submit", type="submit", html=u"<b>提交</b>", **button_style),
        title=u"增加vendor",
        action="/vendor/add"
    )

def vendor_update_vform():
    return btforms.Form(
        btforms.Textbox("vendor_id", rules.not_null, readonly="readonly", description=u"模板ID",required="required", **input_style),
        btforms.Textbox("vendor_desc", rules.not_null, description=u"模板描述",required="required", **input_style),
        btforms.Button("submit", type="submit", html=u"<b>提交</b>", **button_style),
        title=u"修改vendor",
        action="/vendor/update"
    )


vendor_attr_add_form = btforms.Form(
    btforms.Hidden("vendor_id", description=u"vendor id"),
    btforms.Textbox("attr_name", rules.len_of(1, 255), description=u"属性名称", required="required", **input_style),
    btforms.Textbox("attr_value", rules.len_of(1, 255), description=u"属性值", required="required", **input_style),
    btforms.Textbox("attr_desc", rules.len_of(1, 255), description=u"属性描述", required="required", **input_style),
    btforms.Button("submit", type="submit", html=u"<b>提交</b>", **button_style),
    title=u"增加vendor属性",
    action="/vendor/attr/add"
)

vendor_attr_update_form = btforms.Form(
    btforms.Hidden("id", description=u"编号"),
    btforms.Hidden("vendor_id", description=u"vendor id"),
    btforms.Textbox("attr_name", rules.len_of(1, 255), description=u"属性名称", readonly="readonly", **input_style),
    btforms.Textbox("attr_value", rules.len_of(1, 255), description=u"属性值", required="required", **input_style),
    btforms.Textbox("attr_desc", rules.len_of(1, 255), description=u"属性描述", required="required", **input_style),
    btforms.Button("submit", type="submit", html=u"<b>更新</b>", **button_style),
    title=u"修改vendor属性",
    action="/vendor/attr/update"
)

