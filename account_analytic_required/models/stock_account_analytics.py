
from odoo import models, fields


class account_analytics_field(models.Model):
    _inherit = "stock.picking"

    stock_account_analytics = fields.Many2one('account.analytic.account', string="Cuenta analítica")
