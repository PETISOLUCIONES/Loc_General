# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_journals_per_user = fields.Boolean(
        string='Habilitar limite de diarios por usuario',
        help="Habilitar la funcionalidad de limitar diarios por usuario.",
        default=True,
        required=False,
        readonly=False
    )
