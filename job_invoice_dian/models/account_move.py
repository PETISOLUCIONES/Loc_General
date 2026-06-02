from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.queue_job.exception import RetryableJobError
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
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
        Wrapper para queue_job: soporta lotes de facturas.
        Procesa cada factura individualmente para aislar errores.
        """
        for invoice in self:
            if invoice.invoice_status_dian == 'Exitoso':
                continue
            try:
                invoice.action_post1()
            except Exception as e:
                _logger.exception(f"Error en factura {invoice.id}: {str(e)}")

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
        for i in range(0, len(invoices), 10):
            batch = invoices[i:i + 10]
            batch.with_delay(
                channel="root",
                description="DIAN retry lote %d-%d" % (i + 1, min(i + 10, len(invoices))),
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
        for i in range(0, len(invoices), 10):
            batch = invoices[i:i + 10]
            batch.with_delay(
                channel="root",
                description="DIAN schema retry lote %d-%d" % (i + 1, min(i + 10, len(invoices))),
                priority=0,
                max_retries=1,
            )._send_to_dian_safe()

    def _cron_redate_failed_invoices(self):
        from datetime import datetime

        today = fields.Date.today()
        # Calcular los días 1 y 2 del mes actual
        first_day = today.replace(day=1)
        second_day = today.replace(day=2)
        target_dates = [first_day, second_day]

        invoices = self.env['account.move']
        cutoff = datetime.combine(first_day, datetime.min.time()).replace(hour=1)
        for target_date in target_dates:
            invoices |= self.search([
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '=', target_date),
                ('invoice_status_dian', '!=', 'Exitoso'),
                ('create_date', '>=', cutoff),('create_uid', '=', 1),
            ])

        if not invoices:
            return

        today_date = fields.Date.context_today(self)
        self.env.cr.execute(
            "UPDATE account_move SET invoice_date = %s WHERE id = ANY(%s)",
            (today_date, invoices.ids)
        )        # for i in range(0, len(invoices), 10):
        #     batch = invoices[i:i + 10]
        #     batch.with_delay(
        #         channel="root",
        #         description="DIAN redate retry lote %d-%d" % (i + 1, min(i + 10, len(invoices))),
        #         priority=0,
        #         max_retries=1,
        #     )._send_to_dian_safe()




