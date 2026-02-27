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
        if not self.company_id.auto_send_dian and self.move_type in ['out_invoice', 'out_refund']:
            self.with_delay(
                    channel="root",
                    description="DIAN send %s" % (self.name or self.id),
                    priority=0,
                    max_retries=10,).action_post1()
        return res
