# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):

    _inherit = 'res.partner'

    is_customer = fields.Boolean(compute='_compute_is_customer',
                                 inverse='_inverse_is_customer', store=True, string="Is Customer")
    is_vendor = fields.Boolean(compute='_compute_is_vendor',
                               inverse='_inverse_is_vendor', store=True, string="Is Vendor")

    @api.depends('customer_rank')
    def _compute_is_customer(self):
        for rec in self:
            rec.is_customer = True if rec.customer_rank > 0 else False

    def _inverse_is_customer(self):
        for rec in self:
            rec.customer_rank = 1 if rec.is_customer else 0

    @api.depends('supplier_rank')
    def _compute_is_vendor(self):
        for rec in self:
            rec.is_vendor = True if rec.supplier_rank > 0 else False

    def _inverse_is_vendor(self):
        for rec in self:
            rec.supplier_rank = 1 if rec.is_vendor else 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: