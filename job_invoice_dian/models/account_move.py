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
            # Revisa que el action_post haya sido llamado desde un proceso de colas
            if not self.env.context.get('not_queue'):
                self.with_delay(
                        channel="root",
                        description="DIAN send %s" % (self.name or self.id),
                        priority=0,
                        max_retries=1,)._send_to_dian_safe()
        return res

    def _send_to_dian_safe(self):
        """
        Wrapper para queue_job: evita reenvío doble a la DIAN si el job reintenta
        tras una excepción ocurrida *después* de que la DIAN ya aceptó la factura.
        """
        if self.invoice_status_dian and self.invoice_status_dian != 'Fallida':
            return
        self.action_post1()

    def _cron_requeue_failed_dian_jobs(self):
        failed_jobs = self.env['queue.job'].search([
            ('channel', '=', 'root'),
            ('state', '=', 'failed'),
        ])
        failed_jobs.requeue()

    def _cron_retry_dian_connection_errors(self):
        active_jobs = self.env['queue.job'].search([
            ('model_name', '=', 'account.move'),
            ('method_name', 'in', ['action_post1', '_send_to_dian_safe']),
            ('channel', '=', 'root'),
            ('state', 'in', ['pending', 'enqueued', 'started', 'done']),
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
                max_retries=1,
            )._send_to_dian_safe()


    def _cron_send_invoice_failed(self):
        active_jobs = self.env['queue.job'].search([
            ('model_name', '=', 'account.move'),
            ('method_name', '=', '_send_to_dian_safe'),
            ('channel', '=', 'root'),
            ('state', 'in', ['pending', 'enqueued', 'started']),
        ])
        already_queued_ids = [rid for job in active_jobs for rid in job.record_ids]

        invoices = self.search([
            ('id', 'not in', already_queued_ids),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('invoice_status_dian', '=', 'Fallida'),
            ('description_status_dian', 'in', ['Regla: ZB01, Rechazo: Fallo en el esquema XML del archivo', '', False]),
        ])
        for invoice in invoices:
            invoice.with_delay(
                channel="root",
                description="DIAN retry %s" % invoice.name,
                priority=0,
                max_retries=1,
            )._send_to_dian_safe()




