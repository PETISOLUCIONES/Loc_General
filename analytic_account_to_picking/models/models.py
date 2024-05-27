from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange('product_id')
    def onchange_product_id_analytic_acc(self):
        for rec in self:
            order = rec.env['purchase.order'].search([('name', '=', rec.picking_id.origin)])
            if order:
                rec.analytic_account_id = order.account_analytic_id

    @api.constrains('product_id')
    def constrains_to_analytic_acc(self):
        for rec in self:
            order = rec.env['purchase.order'].search([('name', '=', rec.picking_id.origin)])
            if order and not rec.analytic_account_id:
                rec.analytic_account_id = order.account_analytic_id
