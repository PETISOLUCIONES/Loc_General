# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_journals_per_user = fields.Boolean(
        string='Habilitar limite de diarios por usuario',
        help="Habilitar la funcionalidad de limitar diarios por usuario.",
        required=False,
        readonly=False,
        related='company_id.enable_journals_per_user'
    )
