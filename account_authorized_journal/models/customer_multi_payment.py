from odoo import _, exceptions, fields, models, api


class MultiInvoicePayment(models.TransientModel):
    _inherit = "customer.multi.payments"

    journal_id = fields.Many2one('account.journal', required=True, domain= lambda self: [('type', 'in', ('bank', 'cash')), ('id', 'in', self.env.user.account_journal_ids.ids or self.env['account.journal'].search([]).ids)])
