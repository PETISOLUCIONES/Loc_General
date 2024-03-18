# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    order_ref = fields.Char('Order Reference',related='order_id.name')   
    vendor_id = fields.Many2one('res.partner',related='order_id.partner_id')
    qty_to_receive = fields.Float("Pendiente", compute='_compute_qty_to_receive',
                                  store=True,
                                  digits='Product Unit of Measure')

    @api.depends('product_qty', 'qty_received')
    def _compute_qty_to_receive(self):
        for line in self:
            line.qty_to_receive = line.product_qty - line.qty_received


