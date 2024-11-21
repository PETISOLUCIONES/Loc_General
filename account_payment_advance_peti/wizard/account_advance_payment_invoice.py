from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.account_payment_advance_peti.models.account_move import MAP_INVOICE_TYPE_PARTNER_TYPE


class AccountAdvancePaymentInvoice(models.TransientModel):
    _name = 'account.advance.payment.invoice'
    _description = 'Apply Advance Payments'

    journal_id = fields.Many2one('account.journal', string='Diario de aplicacion', required=True)
    date = fields.Date(string='Application Date', required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Tercero', readonly=True)
    partner_type = fields.Selection([('customer', 'Cliente'), ('supplier', 'Proveedor')])
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    invoice_residual = fields.Monetary(string='Total Factura',
                                        currency_field='currency_id', readonly=True)
    advance_payment_total = fields.Monetary(compute='_get_advance_payment_total',
                                            string='Total Anticipo',
                                            currency_field='currency_id')
    advance_payment_residual = fields.Monetary(compute='_get_advance_payment_total',
                                                string='Pagos anticipados restantes',
                                                currency_field='currency_id')
    advance_payment_ids = fields.Many2many('account.payment', 'account_advance_payment_invoice_rel',
                                            'advance_payment_invoice_id', 'payment_id',
                                            'Anticipos', required=True)
    advance_payment_line_ids = fields.Many2many(
        'account.move.line',             
        'advance_payment_line_relation',  
        'advance_payment_id',            
        'move_line_id',             
        string='Anticipos'
    )
    company_id = fields.Many2one('res.company', string='Empresa', required=True, default=lambda self: self.env.user.company_id)

    def _get_default_advance_payment_lines(self):
        """
        Calcula las líneas de pago anticipado por defecto para este modelo.
        """
        # Obtener company_id y partner_id desde el contexto, o desde los valores actuales
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        partner_id = self.env.context.get('partner_id') or self.partner_id.id

        # Verificamos que existan company_id y partner_id
        if company_id and partner_id:
            # Realizamos la búsqueda de las líneas de movimiento de cuenta relacionadas con pagos anticipados
            move_lines = self.env['account.move.line'].search([
                ('company_id', '=', company_id),
                ('account_id.used_for_advance_payment', '=', True),
                ('partner_id', '=', partner_id),
                ('reconciled', '=', False),
                ('move_id.state', '=', 'posted'),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ])
            return [(6, 0, move_lines.ids)]
        return []

    @api.depends('advance_payment_ids','advance_payment_line_ids')
    def _get_advance_payment_total(self):
        for record in self:
            payment_residual = 0.0
            for payment in record.advance_payment_line_ids:
                payment_currency = payment.currency_id.with_context(date=payment.date)
                if record.currency_id != payment_currency:
                    payment_residual += payment_currency.compute(payment.amount_residual,
                                                                    record.currency_id)
                else:
                    payment_residual += payment.amount_residual
            record.advance_payment_total = payment_residual
            record.advance_payment_residual = (payment_residual > record.invoice_residual
                                                and payment_residual - record.invoice_residual
                                                or 0.0)

    @api.onchange('company_id')
    def _onchange_company(self):
        self.journal_id = self.company_id.advance_payment_journal_id.id

    # @api.onchange('company_id','advance_payment_line_ids','journal_id')
    # def _onchange_advance_payment_line_ids(self):
    #     move = self.env['account.move.line'].search([
    #             ('company_id', '=', self.company_id.id),
    #             ('account_id.used_for_advance_payment', '=', True),
    #             ('partner_id', '=', self.partner_id.id),
    #             ('amount_residual', '!=', 0.0),
    #             ('move_id.state', '=', 'posted'),
    #         ])
    #     self.advance_payment_line_ids = [(6, 0,move.ids)]

    def default_get(self, fields):
        rec = super(AccountAdvancePaymentInvoice, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Error de programación: acción del asistente ejecutada sin active_model o active_ids en contexto."))
        if active_model != 'account.move':
            raise UserError(_("Error de programación: el modelo esperado para esta acción es 'account.move'. El proporcionado es '%s'.") % active_model)

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("Solo puede aplicar anticipos para facturas contabilizadas"))
        if any(inv.partner_id != invoices[0].partner_id for inv in invoices):
            raise UserError(_("Para pagar varias facturas a la vez, las facturas deben tener el mismo Tercero."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.move_type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type] for inv in invoices):
            raise UserError(_("No puede mezclar facturas de clientes y facturas de proveedores en un solo pago."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("Para pagar varias facturas a la vez, deben usar la misma moneda."))

        company_id = invoices[0].company_id.id
        partner_id = invoices[0].partner_id.id
        move = self.env['account.move.line'].search([
            ('company_id', '=', company_id),
            ('account_id.used_for_advance_payment', '=', True),
            ('partner_id', '=', partner_id),
            ('reconciled', '=', False),
            ('move_id.state', '=', 'posted'),
            ('name', 'not ilike', 'Advance Payment:'),
            '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
        ])

        rec.update({
            'advance_payment_line_ids': [(6, 0,move.ids)],
            'company_id': company_id,
            'currency_id': invoices[0].currency_id.id,
            'invoice_residual': sum(inv.amount_residual for inv in invoices),
            'partner_id': partner_id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type]
        })
        return rec

    def apply_advance_payment(self):
        for record in self:
            if record.advance_payment_total > record.invoice_residual and len(record.advance_payment_line_ids) > 1:
                error = ('Aplicación múltiple de anticipos que'
                            'exceder el saldo de la factura aún no es compatible')
                raise ValidationError(_(error))

            partner = self.env['res.partner']._find_accounting_partner(record.partner_id)
            invoices = self.env['account.move'].browse(self._context.get('active_ids'))
            invoice_move_lines = invoices.mapped('line_ids').filtered(lambda r: not r.reconciled and r.account_id.account_type in ('asset_receivable', 'liability_payable'))
            date_invoice = min(invoices.mapped('invoice_date'))

            advance_payment_accounts = self.env['account.account']
            advance_payment_lines = {}
            for line in record.advance_payment_line_ids:
                payment_account = line.account_id
                advance_payment_accounts |= payment_account
                if line.id not in advance_payment_lines:
                    advance_payment_lines[line.id] = self.env['account.move.line']
                advance_payment_lines[line.id] |= line

            advance_payment_move_lines = []
            advance_payment_residual = record.advance_payment_total - record.advance_payment_residual
            counterpart_balance = currency_exchange_diff = 0.0
            currency_company = record.company_id.currency_id
            advance_payment_lines_aggregate = self.env['account.move.line']

            for lines in advance_payment_lines.values():
                advance_payment_lines_aggregate |= lines
                for line in lines:
                    balance = abs(line.balance)
                    currency = line.currency_id or currency_company
                    currency_invoice = record.currency_id
                    payment_date = line.date

                    if currency_company != currency_invoice:
                        advance_payment_residual = currency_invoice.with_context(date=payment_date)\
                                                        .compute(advance_payment_residual,
                                                                currency_company)

                    balance_now = balance_used = abs(min(balance, advance_payment_residual))
                    if currency != currency_company and balance:
                        if line.amount_currency:
                            amount_currency = abs(line.amount_currency * (balance_used / balance))
                        else:
                            amount_currency = balance_used
                        balance_now = currency.with_context(date=date_invoice)\
                                        .compute(amount_currency, currency_company)

                    if currency != currency_invoice:
                        balance_now = currency.with_context(date=payment_date)\
                                        .compute(balance_now, currency_invoice)
                        balance_now = currency_invoice.with_context(date=date_invoice)\
                                        .compute(balance_now, currency)

                    counterpart_balance += balance_now
                    currency_exchange_diff += balance_now - balance_used

                    if record.partner_type == 'customer':
                        credit = 0.0
                        debit = balance_used
                        advance_payment_residual -= debit
                    else:
                        debit = 0.0
                        credit = balance_used
                        advance_payment_residual -= credit

                    currency_company = currency_company.with_context(date=payment_date)
                    if currency_company != currency_invoice:
                        advance_payment_residual = currency_company.compute(advance_payment_residual,
                                                                            currency_invoice)

                    if credit or debit:
                        advance_payment_move_lines.append((0, 0, {
                            'name': 'Advance Payment: %s' % ', '.join(lines.mapped('move_id').mapped('name')),
                            'account_id': line.account_id.id,
                            'partner_id': partner.id,
                            'debit': debit,
                            'credit': credit,
                            'payment_id': line.payment_id.id,
                            'advance_account': True,
                        }))
            if counterpart_balance:
                advance_payment_move_lines.append((0, 0, {
                    'name': 'Advance Payment: %s' % ', '.join(invoices.mapped('name')),
                    'account_id': record.partner_type == 'customer' and partner.property_account_receivable_id.id or partner.property_account_payable_id.id,
                    'partner_id': partner.id,
                    'debit': record.partner_type == 'supplier' and counterpart_balance or 0.0,
                    'credit': record.partner_type == 'customer' and counterpart_balance or 0.0,
                    'advance_account': False,
                }))

            if currency_exchange_diff:
                currency_exchange_journal = record.company_id.currency_exchange_journal_id
                if currency_exchange_diff < 0:
                    if record.partner_type == 'supplier':
                        currency_exchange_account = currency_exchange_journal.default_debit_account_id
                        credit = 0.0
                        debit = abs(currency_exchange_diff)
                    else:
                        currency_exchange_account = currency_exchange_journal.default_credit_account_id
                        credit = abs(currency_exchange_diff)
                        debit = 0.0
                else:
                    if record.partner_type == 'supplier':
                        currency_exchange_account = currency_exchange_journal.default_credit_account_id
                        credit = currency_exchange_diff
                        debit = 0.0
                    else:
                        currency_exchange_account = currency_exchange_journal.default_debit_account_id
                        credit = 0.0
                        debit = currency_exchange_diff

                advance_payment_move_lines.append((0, 0, {
                    'name': 'Currency Exchange Difference',
                    'account_id': currency_exchange_account.id,
                    'partner_id': partner.id,
                    'debit': debit,
                    'credit': credit,
                    'advance_account': False,
                }))

            if advance_payment_move_lines:
                move = self.env['account.move'].with_context(skip_validation=True).create({
                    'date': fields.Date.today(),
                    'company_id': record.company_id.id,
                    'journal_id': record.journal_id.id,
                    'line_ids': advance_payment_move_lines,
                })
                move.action_post()

                invoice_payment_move_lines = move.line_ids.filtered(lambda r: not r.reconciled and r.account_id.account_type in ('asset_receivable', 'liability_payable'))
                advance_payment_move_lines = move.line_ids.filtered(lambda r: not r.reconciled and r.account_id in advance_payment_accounts)

                payment_lines = invoice_payment_move_lines + invoice_move_lines
                advance_payment_lines = advance_payment_move_lines + advance_payment_lines_aggregate
                payment_lines.reconcile()
                advance_payment_lines.reconcile()
                move.write({'date': record.date})
    # def apply_advance_payment(self):
    #     for record in self:
    #         if (record.advance_payment_total > record.invoice_residual
    #                 and len(record.advance_payment_ids) > 1):
    #             error = ('Aplicación múltiple de anticipos que'
    #                         'exceder el saldo de la factura aún no es compatible')
    #             raise ValidationError(_(error))

    #         partner = self.env['res.partner']._find_accounting_partner(record.partner_id)
    #         invoices = self.env['account.move'].browse(self._context.get('active_ids'))
    #         invoice_move_lines = invoices.mapped('line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
    #         date_invoice = min(invoices.mapped('invoice_date'))

    #         advance_payment_accounts = self.env['account.account']
    #         payment_move_line = {}
    #         for payment in record.advance_payment_ids:
    #             payment_account = payment.destination_account_id
    #             advance_payment_accounts |= payment_account
    #             if payment.id not in payment_move_line:
    #                 payment_move_line[payment.id] = self.env['account.move.line']
    #             payment_move_line[payment.id] |= payment.move_line_ids.filtered(lambda r: not r.reconciled and r.account_id.used_for_advance_payment == True)
    #             #payment.write({'invoice_ids': [(4, x.id, None) for x in invoices]})

    #         advance_payment_move_lines = []
    #         advance_payment_residual = record.advance_payment_total - record.advance_payment_residual
    #         counterpart_balance = currency_exchange_diff = 0.0
    #         currency_company = record.company_id.currency_id
    #         payment_move_lines = self.env['account.move.line']

    #         for lines in payment_move_line.values():
    #             payment_move_lines |= lines
    #             for line in lines:
    #                 balance = abs(line.balance)
    #                 currency = line.currency_id or currency_company
    #                 currency_invoice = record.currency_id
    #                 payment_date = line.payment_id.date

    #                 if currency_company != currency_invoice:
    #                     advance_payment_residual = currency_invoice.with_context(date=payment_date)\
    #                                                     .compute(advance_payment_residual,
    #                                                             currency_company)

    #                 balance_now = balance_used = min(balance, advance_payment_residual)
    #                 if currency != currency_company and balance:
    #                     if line.amount_currency:
    #                         amount_currency = abs(line.amount_currency * (balance_used / balance))
    #                     else:
    #                         amount_currency = balance_used
    #                     balance_now = currency.with_context(date=date_invoice)\
    #                                     .compute(amount_currency, currency_company)

    #                 if currency != currency_invoice:
    #                     balance_now = currency.with_context(date=payment_date)\
    #                                     .compute(balance_now, currency_invoice)
    #                     balance_now = currency_invoice.with_context(date=date_invoice)\
    #                                     .compute(balance_now, currency)

    #                 counterpart_balance += balance_now
    #                 currency_exchange_diff += balance_now - balance_used

    #                 if record.partner_type == 'customer':
    #                     credit = 0.0
    #                     debit = balance_used
    #                     advance_payment_residual -= debit
    #                 else:
    #                     debit = 0.0
    #                     credit = balance_used
    #                     advance_payment_residual -= credit

    #                 currency_company = currency_company.with_context(date=payment_date)
    #                 if currency_company != currency_invoice:
    #                     advance_payment_residual = currency_company.compute(advance_payment_residual,
    #                                                                         currency_invoice)

    #                 if credit or debit:
    #                     advance_payment_move_lines.append((0, 0, {
    #                         'name': 'Advance Payment: %s' % ', '.join(lines.mapped('move_id').mapped('name')),
    #                         'account_id': line.account_id.id,
    #                         'partner_id': partner.id,
    #                         'debit': debit,
    #                         'credit': credit,
    #                         'payment_id': line.payment_id.id,
    #                         'advance_account': True,
    #                     }))

    #         if counterpart_balance:
    #             advance_payment_move_lines.append((0, 0, {
    #                 'name': 'Advance Payment: %s' % ', '.join(invoices.mapped('name')),
    #                 'account_id': record.partner_type == 'customer' and partner.property_account_receivable_id.id or partner.property_account_payable_id.id,
    #                 'partner_id': partner.id,
    #                 'debit': record.partner_type == 'supplier' and counterpart_balance or 0.0,
    #                 'credit': record.partner_type == 'customer' and counterpart_balance or 0.0,
    #                 'advance_account': False,
    #             }))

    #         if currency_exchange_diff:
    #             currency_exchange_journal = record.company_id.currency_exchange_journal_id
    #             if currency_exchange_diff < 0:
    #                 if record.partner_type == 'supplier':
    #                     currency_exchange_account = currency_exchange_journal.default_debit_account_id
    #                     credit = 0.0
    #                     debit = abs(currency_exchange_diff)
    #                 else:
    #                     currency_exchange_account = currency_exchange_journal.default_credit_account_id
    #                     credit = abs(currency_exchange_diff)
    #                     debit = 0.0
    #             else:
    #                 if record.partner_type == 'supplier':
    #                     currency_exchange_account = currency_exchange_journal.default_credit_account_id
    #                     credit = currency_exchange_diff
    #                     debit = 0.0
    #                 else:
    #                     currency_exchange_account = currency_exchange_journal.default_debit_account_id
    #                     credit = 0.0
    #                     debit = currency_exchange_diff

    #             advance_payment_move_lines.append((0, 0, {
    #                 'name': 'Currency Exchange Difference',
    #                 'account_id': currency_exchange_account.id,
    #                 'partner_id': partner.id,
    #                 'debit': debit,
    #                 'credit': credit,
    #                 'advance_account': False,
    #             }))

    #         if advance_payment_move_lines:
    #             move = self.env['account.move'].with_context(skip_validation=True).create({
    #                 'date': record.date,
    #                 'company_id': record.company_id.id,
    #                 'journal_id': record.journal_id.id,
    #                 'line_ids': advance_payment_move_lines,
    #             })
    #             move.post()

    #             invoice_payment_move_lines = move.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
    #             advance_payment_move_lines = move.line_ids.filtered(lambda r: not r.reconciled and r.account_id in advance_payment_accounts)

    #             (invoice_payment_move_lines + invoice_move_lines).reconcile()
    #             (advance_payment_move_lines + payment_move_lines).reconcile()
