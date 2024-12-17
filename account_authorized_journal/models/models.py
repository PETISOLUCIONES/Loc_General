# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import ast


class ResUsers(models.Model):
    _inherit = 'res.users'

    account_journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Diarios habilitados'
    )

    @api.constrains('account_journal_ids')
    def _check_number_of_journals(self):
        for user in self:
            if len(user.account_journal_ids) > 2:
                raise ValidationError(_("No puede asignar más de 2 diarios por usuario."))


class JournalDomainExtensionMixin(models.AbstractModel):
    _name = 'journal.domain.extension.mixin'
    _description = 'Mixin para extender dominios de campos Many2one que apuntan a account.journal'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Modificar los dominios de los campos relacionados con account.journal.
        """
        res = super(JournalDomainExtensionMixin, self).fields_get(allfields=allfields, attributes=attributes)
        for field_name, field_attrs in res.items():
            # Verificar si el campo es de tipo relación y está relacionado con account.journal
            if field_attrs.get('type') in ['many2one', 'many2many', 'one2many'] and field_attrs.get('relation') == 'account.journal':
                # Agregar o modificar el dominio según la lógica deseada
                user_journals = self.env.user.account_journal_ids.ids
                domain = "('id', 'in', %s)" % user_journals
                if 'domain' in field_attrs and field_attrs['domain']:
                    # Combinar dominios existentes si es necesario
                    field_attrs['domain'] = f"({field_attrs['domain']}) + ([{domain}])"
                else:
                    # Asignar el nuevo dominio
                    field_attrs['domain'] = f"[{domain}]"
        return res

    def _get_view(self, view_id=None, view_type='form', **options):
        """
        Modificar la vista para extender los dominios de los campos relacionados con account.journal.
        """
        # Obtener la definición original de la vista
        arch, view = super(JournalDomainExtensionMixin, self)._get_view(view_id=view_id, view_type=view_type, **options)

        if view_type in ['form', 'tree']:
            # Obtener los diarios asignados al usuario actual
            user_journals = self.env.user.account_journal_ids.ids
            if user_journals:
                # Obtener la información de todos los campos del modelo
                fields_info = self.fields_get()
                # Preparar la condición adicional del dominio
                extra_condition = "('id', 'in', %s)" % user_journals

                # Recorrer todos los campos para identificar aquellos que apuntan a account.journal
                for field_name, field_attrs in fields_info.items():
                    field_type = field_attrs.get('type')
                    field_relation = field_attrs.get('relation')

                    # Verificar si el campo es una relación con account.journal
                    if field_type in ['many2one', 'many2many', 'one2many'] and field_relation == 'account.journal':
                        # Buscar este campo en la vista
                        field_nodes = arch.xpath("//field[@name='%s']" % field_name)
                        for field_node in field_nodes:
                            current_domain_str = field_node.get('domain')
                            if current_domain_str:
                                # Si ya existía un dominio, agregar la condición al final
                                final_domain_str = "[(" + current_domain_str[1:-1] + "), " + extra_condition + "]"
                                # Asignar el dominio combinado al campo en la vista
                                field_node.set('domain', final_domain_str)
        # Retornar la vista modificada
        return arch, view

    @api.model
    def create(self, vals):
        """
        Crear un nuevo registro en el modelo.
        """
        # Validar que los diarios asignados al usuario actual sean válidos
        user_journals = self.env.user.account_journal_ids
        fields_info = self.fields_get()
        for field_name, field_attrs in fields_info.items():
            # Verificar si el campo es de tipo relación y está relacionado con account.journal
            if field_attrs.get('type') in ['many2one', 'many2many', 'one2many'] and field_attrs.get('relation') == 'account.journal':
                # Validar que los diarios asignados al usuario actual sean válidos
                if field_name in vals and vals[field_name] and vals[field_name] not in user_journals.ids:
                    journal = self.env['account.journal'].browse(vals[field_name]) if isinstance(vals[field_name], int) else False
                    raise ValidationError(
                        f"No tiene permiso para seleccionar el diario '{journal and journal.name or vals[field_name]}'.\n\n"
                        f"Sus diarios habilitados son: {(', '.join(j.name for j in user_journals)) or 'Ninguno'}"
                    )
        # Retornar el resultado del método original de la superclase
        return super(JournalDomainExtensionMixin, self).create(vals)

    def write(self, vals):
        """
        Modificar uno o varios registros del modelo.
        """
        # Validar que los diarios asignados al usuario actual sean válidos
        user_journals = self.env.user.account_journal_ids
        fields_info = self.fields_get()
        for field_name, field_attrs in fields_info.items():
            # Verificar si el campo es de tipo relación y está relacionado con account.journal
            if field_attrs.get('type') in ['many2one', 'many2many', 'one2many'] and field_attrs.get('relation') == 'account.journal':
                # Validar que los diarios asignados al usuario actual sean válidos
                if field_name in vals and vals[field_name] and vals[field_name] not in user_journals.ids:
                    journal = self.env['account.journal'].browse(vals[field_name]) if isinstance(vals[field_name], int) else False
                    raise ValidationError(
                        f"No tiene permiso para seleccionar el diario '{journal and journal.name or vals[field_name]}'.\n\n"
                        f"Sus diarios habilitados son: {(', '.join(j.name for j in user_journals)) or 'Ninguno'}"
                    )
        # Llamar al método original de la superclase
        return super(JournalDomainExtensionMixin, self).write(vals)


class AccruedExpenseRevenue(models.TransientModel):
    _name = 'account.accrued.orders.wizard'
    _inherit = ['account.accrued.orders.wizard', 'journal.domain.extension.mixin']


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['account.analytic.line', 'journal.domain.extension.mixin']


class AccountAsset(models.Model):
    _name = 'account.asset'
    _inherit = ['account.asset', 'journal.domain.extension.mixin']


class AutomaticEntryWizard(models.TransientModel):
    _name = 'account.automatic.entry.wizard'
    _inherit = ['account.automatic.entry.wizard', 'journal.domain.extension.mixin']


class AccountBankStatement(models.Model):
    _name = 'account.bank.statement'
    _inherit = ['account.bank.statement', 'journal.domain.extension.mixin']


class AccountBankStatementLine(models.Model):
    _name = 'account.bank.statement.line'
    _inherit = ['account.bank.statement.line', 'journal.domain.extension.mixin']


class AccountBankStatementLineTransient(models.TransientModel):
    _name = 'account.bank.statement.line.transient'
    _inherit = ['account.bank.statement.line.transient', 'journal.domain.extension.mixin']


class AccountDebitNote(models.TransientModel):
    _name = 'account.debit.note'
    _inherit = ['account.debit.note', 'journal.domain.extension.mixin']


class FinancialYearOpeningWizard(models.TransientModel):
    _name = 'account.financial.year.op'
    _inherit = ['account.financial.year.op', 'journal.domain.extension.mixin']


class AccountInvoiceReport(models.Model):
    _name = 'account.invoice.report'
    _inherit = ['account.invoice.report', 'journal.domain.extension.mixin']


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['account.journal', 'journal.domain.extension.mixin']


class AccountJournalGroup(models.Model):
    _name = 'account.journal.group'
    _inherit = ['account.journal.group', 'journal.domain.extension.mixin']


class AccountMissingTransaction(models.TransientModel):
    _name = 'account.missing.transaction.wizard'
    _inherit = ['account.missing.transaction.wizard', 'journal.domain.extension.mixin']


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'journal.domain.extension.mixin']


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'journal.domain.extension.mixin']


class AccountMoveReversal(models.TransientModel):
    _name = 'account.move.reversal'
    _inherit = ['account.move.reversal', 'journal.domain.extension.mixin']


class MulticurrencyRevaluationWizard(models.TransientModel):
    _name = 'account.multicurrency.revaluation.wizard'
    _inherit = ['account.multicurrency.revaluation.wizard', 'journal.domain.extension.mixin']


class AccountOnlineAccount(models.Model):
    _name = 'account.online.account'
    _inherit = ['account.online.account', 'journal.domain.extension.mixin']


class AccountOnlineLink(models.Model):
    _name = 'account.online.link'
    _inherit = ['account.online.link', 'journal.domain.extension.mixin']


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'journal.domain.extension.mixin']


class AccountPaymentMethodLine(models.Model):
    _name = 'account.payment.method.line'
    _inherit = ['account.payment.method.line', 'journal.domain.extension.mixin']


class AccountPaymentMode(models.Model):
    _name = 'account.payment.mode'
    _inherit = ['account.payment.mode', 'journal.domain.extension.mixin']


class AccountReconcileModel(models.Model):
    _name = 'account.reconcile.model'
    _inherit = ['account.reconcile.model', 'journal.domain.extension.mixin']


class AccountReconcileModelLine(models.Model):
    _name = 'account.reconcile.model.line'
    _inherit = ['account.reconcile.model.line', 'journal.domain.extension.mixin']


class AccountReconcileWizard(models.TransientModel):
    _name = 'account.reconcile.wizard'
    _inherit = ['account.reconcile.wizard', 'journal.domain.extension.mixin']


class SetupBarBankConfigWizard(models.TransientModel):
    _name = 'account.setup.bank.manual.config'
    _inherit = ['account.setup.bank.manual.config', 'journal.domain.extension.mixin']


class TransferModel(models.Model):
    _name = 'account.transfer.model'
    _inherit = ['account.transfer.model', 'journal.domain.extension.mixin']


class BankRecWidget(models.Model):
    _name = 'bank.rec.widget'
    _inherit = ['bank.rec.widget', 'journal.domain.extension.mixin']


class CommissionMakeInvoice(models.TransientModel):
    _name = 'commission.make.invoice'
    _inherit = ['commission.make.invoice', 'journal.domain.extension.mixin']


class MultiInvoicePayment(models.TransientModel):
    _name = 'customer.multi.payments'
    _inherit = ['customer.multi.payments', 'journal.domain.extension.mixin']


class WorkflowActionRule(models.Model):
    _name = 'documents.workflow.rule'
    _inherit = ['documents.workflow.rule', 'journal.domain.extension.mixin']


class GeneralLedgerReportWizard(models.TransientModel):
    _name = 'general.ledger.report.wizard'
    _inherit = ['general.ledger.report.wizard', 'journal.domain.extension.mixin']


class HrExpense(models.Model):
    _name = 'hr.expense'
    _inherit = ['hr.expense', 'journal.domain.extension.mixin']


class HrExpenseSheet(models.Model):
    _name = 'hr.expense.sheet'
    _inherit = ['hr.expense.sheet', 'journal.domain.extension.mixin']


class JournalLedgerReportWizard(models.TransientModel):
    _name = 'journal.ledger.report.wizard'
    _inherit = ['journal.ledger.report.wizard', 'journal.domain.extension.mixin']


class PaymentProvider(models.Model):
    _name = 'payment.provider'
    _inherit = ['payment.provider', 'journal.domain.extension.mixin']


class PosConfig(models.Model):
    _name = 'pos.config'
    _inherit = ['pos.config', 'journal.domain.extension.mixin']


class PosOrder(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order', 'journal.domain.extension.mixin']


class PosPaymentMethod(models.Model):
    _name = 'pos.payment.method'
    _inherit = ['pos.payment.method', 'journal.domain.extension.mixin']


class PosSession(models.Model):
    _name = 'pos.session'
    _inherit = ['pos.session', 'journal.domain.extension.mixin']


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'journal.domain.extension.mixin']


class PosOrderReport(models.Model):
    _name = 'report.pos.order'
    _inherit = ['report.pos.order', 'journal.domain.extension.mixin']


class Company(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'journal.domain.extension.mixin']


class ResConfigSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = ['res.config.settings', 'journal.domain.extension.mixin']


class ResPartnerBank(models.Model):
    _name = 'res.partner.bank'
    _inherit = ['res.partner.bank', 'journal.domain.extension.mixin']


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'journal.domain.extension.mixin']


class StockValuationLayerRevaluation(models.TransientModel):
    _name = 'stock.valuation.layer.revaluation'
    _inherit = ['stock.valuation.layer.revaluation', 'journal.domain.extension.mixin']


class Warehouse(models.Model):
    _name = 'stock.warehouse'
    _inherit = ['stock.warehouse', 'journal.domain.extension.mixin']


class TrialBalanceReport(models.TransientModel):
    _name = 'trial.balance.report'
    _inherit = ['trial.balance.report', 'journal.domain.extension.mixin']


class TrialBalanceReportWizard(models.TransientModel):
    _name = 'trial.balance.report.wizard'
    _inherit = ['trial.balance.report.wizard', 'journal.domain.extension.mixin']


# class AccountBalancePartnerFilter(models.TransientModel):
#     _name = 'account.balance.partner.filter'
#     _inherit = ['account.balance.partner.filter', 'journal.domain.extension.mixin']


# class account_balance_report_filters(models.TransientModel):
#     _name = 'account.balance.report.filters'
#     _inherit = ['account.balance.report.filters', 'journal.domain.extension.mixin']


# class AccountLoan(models.Model):
#     _name = 'account.loan'
#     _inherit = ['account.loan', 'journal.domain.extension.mixin']


# class AccountLoanIncreaseAmount(models.TransientModel):
#     _name = 'account.loan.increase.amount'
#     _inherit = ['account.loan.increase.amount', 'journal.domain.extension.mixin']


# class AccountLoanLine(models.Model):
#     _name = 'account.loan.line'
#     _inherit = ['account.loan.line', 'journal.domain.extension.mixin']


# class AccountLoanPost(models.TransientModel):
#     _name = 'account.loan.post'
#     _inherit = ['account.loan.post', 'journal.domain.extension.mixin']


# class DocumentsFolderSetting(models.Model):
#     _name = 'documents.account.folder.setting'
#     _inherit = ['documents.account.folder.setting', 'journal.domain.extension.mixin']


# class ExpenseSampleRegister(models.TransientModel):
#     _name = 'expense.sample.register'
#     _inherit = ['expense.sample.register', 'journal.domain.extension.mixin']


# class hr_closing_configuration_header(models.Model):
#     _name = 'hr.closing.configuration.header'
#     _inherit = ['hr.closing.configuration.header', 'journal.domain.extension.mixin']


# class nom_payroll_flat_file_backup(models.Model):
#     _name = 'nom.payroll.flat.file.backup'
#     _inherit = ['nom.payroll.flat.file.backup', 'journal.domain.extension.mixin']


# class HrLoan(models.Model):
#     _name = 'hr.loan'
#     _inherit = ['hr.loan', 'journal.domain.extension.mixin']


# class HrLoanType(models.Model):
#     _name = 'hr.loan.type'
#     _inherit = ['hr.loan.type', 'journal.domain.extension.mixin']


# class HrPayrollAnticipo(models.Model):
#     _name = 'hr.payroll.advance'
#     _inherit = ['hr.payroll.advance', 'journal.domain.extension.mixin']


# class hr_payroll_flat_file(models.TransientModel):
#     _name = 'hr.payroll.flat.file'
#     _inherit = ['hr.payroll.flat.file', 'journal.domain.extension.mixin']


# class hr_payroll_posting(models.Model):
#     _name = 'hr.payroll.posting'
#     _inherit = ['hr.payroll.posting', 'journal.domain.extension.mixin']


# class HrPayrollStructure(models.Model):
#     _name = 'hr.payroll.structure'
#     _inherit = ['hr.payroll.structure', 'journal.domain.extension.mixin']


# class ImportXML(models.TransientModel):
#     _name = 'import.xml'
#     _inherit = ['import.xml', 'journal.domain.extension.mixin']


# class SaleOrderTemplate(models.Model):
#     _name = 'sale.order.template'
#     _inherit = ['sale.order.template', 'journal.domain.extension.mixin']


# class StockLandedCost(models.Model):
#     _name = 'stock.landed.cost'
#     _inherit = ['stock.landed.cost', 'journal.domain.extension.mixin']
