# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    enable_journals_per_user = fields.Boolean(
        string='Habilitar limite de diarios por usuario',
        help="Habilitar la funcionalidad de limitar diarios por usuario.",
        required=False,
        readonly=False,
        related='company_id.enable_journals_per_user'
    )
    account_journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Diarios habilitados'
    )
