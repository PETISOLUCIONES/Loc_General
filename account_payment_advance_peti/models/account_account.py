from odoo import api, fields, models


class Account(models.Model):
    _inherit = 'account.account'

    used_for_advance_payment = fields.Boolean()

    @api.onchange('used_for_advance_payment')
    def onchange_used_for_advance_payment(self):
        if self.used_for_advance_payment:
            self.reconcile = self.used_for_advance_payment
