from odoo import api, fields, models

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    advance_payment_ids = fields.Many2many('account.payment', 
    compute='_compute_advance_payments'
    )
    advance_payment_count = fields.Integer(compute='_compute_advance_payments',
    string='advance payment?')
    has_advance_payment = fields.Boolean(compute='_has_advance_payment', 
    string='Has advance payment?')

    @api.depends('line_ids')
    def _compute_advance_payments(self):
        invoices = self.filtered(lambda i: i.move_type in ('out_invoice', 'in_invoice'))

        (self - invoices).update({
            'advance_payment_ids': False,
            'advance_payment_count': 0,
        })

        for invoice in self.filtered(lambda i: i.move_type in ('out_invoice', 'in_invoice')):
            lines = invoice.line_ids
            lines |= lines.matched_debit_ids.debit_move_id | lines.matched_credit_ids.credit_move_id

            lines = lines.move_id.line_ids
            lines |= lines.matched_debit_ids.debit_move_id | lines.matched_credit_ids.credit_move_id

            invoice.advance_payment_ids = lines.filtered(lambda line: line.account_id.used_for_advance_payment).mapped('payment_id')
            invoice.advance_payment_count = len(invoice.advance_payment_ids)

    def _has_advance_payment(self):
        for invoice in self:
            move = self.env['account.move.line'].search([
                ('company_id', '=', self.company_id.id),
                ('account_id.used_for_advance_payment', '=', True),
                ('partner_id', '=', self.partner_id.id),
                ('amount_residual', '!=', 0.0),
                ('move_id.state', '=', 'posted'),
            ])
            advance_payment_args = [
                ('company_id', '=', invoice.company_id.id),
                ('advance', '=', True),
                ('partner_id', '=', invoice.partner_id.id),
                ('partner_type', '=', MAP_INVOICE_TYPE_PARTNER_TYPE.get(invoice.move_type, False)),
                ('residual', '>', 0.0),
                ('state', '=', 'posted'),
            ]
            if self.env['account.payment'].search(advance_payment_args) or move:
                invoice.has_advance_payment = True
            else:
                invoice.has_advance_payment = False

    @api.model
    def _cleanup_write_orm_values(self, record, vals):
        partner_type = False
        if record._name == 'account.payment' and record.advance:
            partner_type = record.partner_type
        if record._name == 'account.payment.detail' and record.account_id.used_for_advance_payment:
            partner_type = record.partner_type
        cleaned_vals = super()._cleanup_write_orm_values(record, vals)

        if record._name == 'account.payment' and record.advance and partner_type:
            cleaned_vals['partner_type'] = partner_type
        return cleaned_vals

    def js_remove_outstanding_partial(self, partial_id):
        self.ensure_one()
        partial = self.env['account.partial.reconcile'].browse(partial_id)
        lines = partial.debit_move_id | partial.credit_move_id
        lines |= lines.mapped('move_id.line_ids')

        result = super().js_remove_outstanding_partial(partial_id)

        # Remove advance payment journal entries
        for advance_payment_move in lines.filtered(lambda line: line.account_id.used_for_advance_payment).move_id:
            advance_payment_move.button_draft()
            advance_payment_move.button_cancel()
            advance_payment_move.with_context(force_delete=True).unlink()

        return result


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    advance_account = fields.Boolean(string='Is advance payment?', default=False)
