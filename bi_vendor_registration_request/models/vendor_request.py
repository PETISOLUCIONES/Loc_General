# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class VendorRegistrationRequest(models.Model):
    _name = "vendor.registration.request"
    _description="registration request description"

    name = fields.Char("Name")
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    street = fields.Char("Street")
    city = fields.Char("City")
    zip = fields.Char("ZipCode")
    link = fields.Char("Website Link")
    country = fields.Many2one('res.country', "Country", readonly=True)
    state_id = fields.Many2one('res.country.state', string='State')
    state_city = fields.Char("state")
    state = fields.Selection([('to_approve', 'To Approve'), ('approve', 'Approved'), ('reject','Rejected')], string='Status', default='to_approve')
    types = fields.Selection([('individual', 'Individual'), ('company', 'Company')], string='Vendor type')
    vendor_image = fields.Image("Image")
    child_ids = fields.One2many('vendor.child', 'parent_id', string="Contacts")
    vendor_id = fields.Many2one('res.partner', string="Vendor")

    def action_vendor_view(self):
        self.ensure_one()
        for rec in self:
            if rec.vendor_id:
                return {
                    'name': _('Vendor'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'res.partner',
                    'res_id': rec.vendor_id.id,
                }
            
    def create_vendor(self):
        self.state = 'approve'
        template_id = self.env.ref('bi_vendor_registration_request.create_vendor_email_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        is_company = False
        if self.types == 'company':
            is_company = True
        if self.name:
            vals = {
                'name': self.name,
                'email': self.email,
                'phone': self.phone,
                'mobile': self.mobile,
                'street': self.street,
                'city': self.city,
                'zip': self.zip,
                'website': self.link,
                'country_id': self.country.id,
                'state_id': self.state_id.id,
                'image_1920': self.vendor_image,
                'is_company': is_company,
            }
            vendor_req_obj = self.env['res.partner'].sudo().create(vals)
            if is_company:
                for child in self.child_ids:
                    child_vals = {
                        'name':child.name,
                        'email': child.email,
                        'phone': child.phone,
                        'parent_id': vendor_req_obj.id,
                    }
                    self.env['res.partner'].sudo().create(child_vals)
            self.update({'vendor_id': vendor_req_obj.id})
            return vendor_req_obj


class VendorChild(models.Model):
    _name = "vendor.child"
    _description="vendor child description"
    
    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    phone = fields.Char(string="phone")
    parent_id = fields.Many2one('vendor.registration.request', string="Parent")