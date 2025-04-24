from datetime import datetime, date, timedelta
import logging

from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account')

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        # Récupérer la commande d'achat liée à cette ligne
        purchase_order = self.env['purchase.order'].browse(vals.get('order_id'))

        # Si la commande d'achat a un compte analytique, l'appliquer à la ligne de commande
        if purchase_order.account_analytic_id:
            vals['analytic_distribution'] = {purchase_order.account_analytic_id.id: 100.0}

        return super(PurchaseOrderLine, self).create(vals)