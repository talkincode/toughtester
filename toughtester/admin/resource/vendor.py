#!/usr/bin/env python
# coding:utf-8
import cyclone.web
from toughlib import utils
from toughtester.admin.base import BaseHandler, MenuRes
from toughlib.permit import permit
from toughtester import models
from toughtester.admin.resource import vendor_form


@permit.route(r"/vendor", u"Radius模板管理", MenuRes, order=5.0000, is_menu=True)
class VendorHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.render("vendor_list.html", page_data=self.get_page_data(self.db.query(models.TTVendor)))

@permit.route(r"/vendor/detail", u"Radius模板详情", MenuRes, order=5.0001)
class VendorDetailHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        vendor_id = self.get_argument("vendor_id")
        vendor = self.db.query(models.TTVendor).get(vendor_id)
        attrs = self.db.query(models.TTVendorAttr).filter_by(vendor_id=vendor.vendor_id)
        self.render("vendor_detail.html", vendor=vendor, attrs=attrs)


@permit.route(r"/vendor/add", u"Radius模板新增", MenuRes, order=5.0002)
class AddHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.render("base_form.html", form=vendor_form.vendor_add_vform())

    @cyclone.web.authenticated
    def post(self):
        form = vendor_form.vendor_add_vform()
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)
        if self.db.query(models.TTVendor.vendor_id).filter_by(vendor_id=form.d.vendor_id).count() > 0:
            return self.render("base_form.html", form=form, msg=u"vendor已经存在")
        vendor = models.TTVendor()
        vendor.vendor_id = form.d.vendor_id
        vendor.vendor_desc = form.d.vendor_desc
        self.db.add(vendor)
        self.db.commit()
        self.redirect("/vendor",permanent=False)

@permit.route(r"/vendor/update", u"Radius模板修改", MenuRes, order=5.0003)
class UpdateHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        vendor_id = self.get_argument("vendor_id")
        form = vendor_form.vendor_update_vform()
        form.fill(self.db.query(models.TTVendor).get(vendor_id))
        return self.render("base_form.html", form=form)

    def post(self):
        form = vendor_form.vendor_update_vform(s)
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)
        vendor = self.db.query(models.TTVendor).get(form.d.vendor_id)
        vendor.vendor_desc = form.d.vendor_desc
        self.db.commit()
        self.redirect("/vendor",permanent=False)

@permit.route(r"/vendor/delete", u"Radius模板删除", MenuRes, order=5.0004)
class DeleteHandler(BaseHandler):

    @cyclone.web.authenticated
    def post(self):
        vendor_id = self.get_argument("vendor_id")
        vendor = self.db.query(models.TTVendor).filter_by(id=vendor_id).first()
        self.db.query(models.TTVendor).filter_by(vendor_id=vendor_id).delete()
        self.db.query(models.TTVendorAttr).filter_by(vendor_id=vendor_id).delete()
        self.db.commit()
        return self.render_json(code=0, msg=u"删除Vendor成功!")

@permit.route(r"/vendor/attr/add", u"Vendor属性新增", MenuRes, order=5.0005)
class VendorAttrAddHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        vendor_id = self.get_argument("vendor_id")
        if self.db.query(models.TTVendor).filter_by(vendor_id=vendor_id).count() == 0:
            return self.render_error(msg=u"Vendor不存在")

        form = vendor_form.vendor_attr_add_form()
        form.vendor_id.set_value(vendor_id)
        self.render("base_form.html", form=form)

    @cyclone.web.authenticated
    def post(self):
        form = vendor_form.vendor_attr_add_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form,html", form=form)

        vendor_attr = models.TTVendorAttr()
        vendor_attr.vendor_id = form.d.vendor_id
        vendor_attr.attr_name = form.d.attr_name
        vendor_attr.attr_value = form.d.attr_value
        vendor_attr.attr_desc = form.d.attr_desc
        self.db.add(vendor_attr)

        self.db.commit()
        self.redirect("/vendor/detail?vendor_id=%s" % form.d.vendor_id)

@permit.route(r"/vendor/attr/update", u"Vendor属性修改", MenuRes, order=5.0006)
class VendorAttrUpdateHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        attr_id = self.get_argument("attr_id")
        attr = self.db.query(models.TTVendorAttr).get(attr_id)
        form = vendor_form.vendor_attr_update_form()
        form.fill(attr)
        self.render("base_form.html", form=form)

    @cyclone.web.authenticated
    def post(self, *args, **kwargs):
        form = vendor_form.vendor_attr_update_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form,html", form=form)

        vendor_attr = self.db.query(models.TTVendorAttr).get(form.d.vendor_id)
        vendor_attr.attr_name = form.d.attr_name
        vendor_attr.attr_value = form.d.attr_value
        vendor_attr.attr_desc = form.d.attr_desc
        self.db.commit()
        self.redirect("/vendor/detail?vendor_id=%s" % form.d.vendor_id)

@permit.route(r"/vendor/attr/delete", u"Vendor属性删除", MenuRes, order=5.0007)
class VendorAttrDeleteHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        attr_id = self.get_argument("attr_id")
        attr = self.db.query(models.TTVendorAttr).get(attr_id)
        self.db.query(models.TTVendorAttr).filter_by(id=attr_id).delete()
        self.db.commit()
        self.redirect("/vendor/detail?vendor_id=%s" % attr.vendor_id)




