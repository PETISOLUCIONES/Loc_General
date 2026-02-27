from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
        Sobrescribe el método action_post para controlar el envío a DIAN según configuración
        """
        # Si la configuración de envío automático está activa, usar action_post1
        res = super(AccountMove, self).action_post()
        if not self.company_id.auto_send_dian and self.move_type in ['out_invoice'] and self.subscription_order_id:
            self.with_delay(
                    channel="root",
                    description="DIAN send %s" % (self.name or self.id),
                    priority=0,
                    max_retries=10,).action_post1()
        return res

    def _cron_requeue_failed_dian_jobs(self):
        failed_jobs = self.env['queue.job'].search([
            ('channel', '=', 'root'),
            ('state', '=', 'failed'),
        ])
        failed_jobs.requeue()

    def _cron_retry_dian_connection_errors(self):
        active_jobs = self.env['queue.job'].search([
            ('model_name', '=', 'account.move'),
            ('method_name', '=', 'action_post1'),
            ('channel', '=', 'root'),
            ('state', 'in', ['pending', 'enqueued', 'started']),
        ])
        already_queued_ids = [rid for job in active_jobs for rid in job.record_ids]

        invoices = self.search([
            ('id', 'not in', already_queued_ids),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice']),
            ('invoice_status_dian', '=', 'Fallida'),
            ('description_status_dian', 'not like', 'Regla:'),
        ])
        for invoice in invoices:
            invoice.with_delay(
                channel="root",
                description="DIAN retry %s" % invoice.name,
                priority=0,
                max_retries=10,
            ).action_post1()
