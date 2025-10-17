# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

import re
from odoo import api, models, fields, _
from odoo.osv import expression

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', order=None, limit=100, name_get_uid=None):
        args = args or []
        product_ids = []

        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            if operator in positive_operators:
                product_ids = self._search([('default_code', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid) or \
                              self._search([('barcode', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)

            if not product_ids:
                product_ids = self._search(args + [('default_code', operator, name)], limit=limit) or \
                              self._search(args + [('name', operator, name)], limit=limit)

            if not product_ids:
                ptrn = re.search(r'(\[(.*?)\])', name)
                if ptrn:
                    product_ids = self._search([('default_code', '=', ptrn.group(2))] + args, limit=limit,
                                               access_rights_uid=name_get_uid)

            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('partner_id', '=', self._context.get('partner_id')),
                    '|', ('product_code', operator, name), ('product_name', operator, name)],
                    access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                               access_rights_uid=name_get_uid)

            if not product_ids and self._context.get('pricelist'):
                pricelist = self.env['product.pricelist'].browse(self._context.get('pricelist'))
                product_list = []
                for record in pricelist.item_ids:
                    if record.applied_on == '0_product_variant':
                        product_list.extend(record.product_id.ids)
                    elif record.applied_on == '3_global':
                        product_list.extend(self.env['product.product'].ids)
                    elif record.applied_on == '2_product_category':
                        product_list.extend(self.env['product.product'].search([('categ_id', 'child_of', record.categ_id.id)]).ids)
                    elif record.applied_on == '1_product':
                        product_list.extend(self.env['product.product'].search([('product_tmpl_id', '=', record.product_tmpl_id.id)]).ids)

                if product_list:
                    domain = [('id', 'in', product_list)]
                    product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)

        return product_ids


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    categ_custom_ids = fields.One2many('product.pricelist.item', string='Item', related='order_id.pricelist_id.item_ids')
    product_id_domain = fields.Char(compute="_compute_product_domain")
    product_tmpl_id_domain = fields.Char(compute="_compute_product_domain")

    @api.onchange('categ_custom_ids')
    def _compute_product_domain(self):
        for rec in self:
            product_list = []
            if self.categ_custom_ids:
                for record in self.categ_custom_ids:
                    if record.applied_on == '0_product_variant':
                        product_list.extend(record.product_id.ids)
                    elif record.applied_on == '3_global':
                        product_list.extend(self.env['product.product'].ids)
                    elif record.applied_on == '2_product_category':
                        product_list.extend(self.env['product.product'].search([('categ_id', 'child_of', record.categ_id.id)]).ids)
                    elif record.applied_on == '1_product':
                        product_list.extend(self.env['product.product'].search([('product_tmpl_id', '=', record.product_tmpl_id.id)]).ids)

            if product_list:
                rec.product_id_domain = [('id', 'in', product_list)]
                rec.product_tmpl_id_domain = [('id', 'in', [p.product_tmpl_id.id for p in self.env['product.product'].browse(product_list)])]
            else:
                rec.product_id_domain = rec.product_tmpl_id_domain = []

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {'product_uom': self.product_id.uom_id}
        if not self.product_uom or self.product_uom.id != self.product_id.uom_id.id:
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty', self.product_uom_qty),
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}
        if product.sale_line_warn != 'no-message':
            result['warning'] = {'title': _("Warning for %s") % product.name, 'message': product.sale_line_warn_msg}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        vals['name'] = product.display_name
        if product.description_sale:
            vals['name'] += '\n' + product.description_sale

        self._compute_tax_id()
        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(), product.taxes_id, self.tax_id, self.company_id)

        self.update(vals)
        return result
