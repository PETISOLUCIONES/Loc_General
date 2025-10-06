from odoo import models, fields
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    def get_invoice_line_dict(self, index):
        line_dict = super(AccountMove, self).get_invoice_line_dict(index)
        invoice_type = self.move_id.GetInvoiceType()
        if invoice_type in ['05', '95'] and line_dict:
            line_dict['DocPeriod'] = self.move_id.doc_period.code if self.move_id.doc_period.code else ' '
            line_dict['PurchaseDate'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        return line_dict