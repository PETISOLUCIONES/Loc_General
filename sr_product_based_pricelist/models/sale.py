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
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = list(self._search([('default_code', '=', name)] + domain, limit=limit, order=order))
                if not product_ids:
                    product_ids = list(self._search([('barcode', '=', name)] + domain, limit=limit, order=order))
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = list(self._search(domain + [('default_code', operator, name)], limit=limit, order=order))
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(domain + [('name', operator, name), ('id', 'not in', product_ids)],
                                                limit=limit2, order=order)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain2 = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain2 = expression.AND([domain, domain2])
                product_ids = list(self._search(domain2, limit=limit, order=order))
            if not product_ids and operator in positive_operators:
                ptrn = re.compile(r'(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = list(
                        self._search([('default_code', '=', res.group(2))] + domain, limit=limit, order=order))
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('partner_id', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                               order=order)
            if not product_ids and self._context.get('partner_id'):
                pricelist = self.env['product.pricelist'].browse(self._context.get('pricelist'))
                product_list = []
                for record in pricelist.item_ids:
                    if record.applied_on == '0_product_variant':
                        product_list.extend(record.product_id.ids)
                    elif record.applied_on == '3_global':
                        product_list.extend(self.env['product.product'].ids)
                    elif record.applied_on == '2_product_category':
                        product_list.extend(
                            self.env['product.product'].search([('categ_id', 'child_of', record.categ_id.id)]).ids)
                    elif record.applied_on == '1_product':
                        product_list.extend(self.env['product.product'].search(
                            [('product_tmpl_id', '=', record.product_tmpl_id.id)]).ids)

                if product_list:
                    domain = [('id', 'in', product_list)]
                    product_ids = self._search(domain, limit=limit)
        else:
            product_ids = self._search(domain, limit=limit, order=order)
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
