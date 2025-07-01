# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    allowed_for_user = fields.Boolean(
        string="Permitido para el usuario",
        compute="_compute_allowed_for_user",
        # precompute=True,
        # store=True,
        # readonly=True,
        # index=True,
        help="True si el diario está en la lista del usuario o si el usuario no tiene ninguno configurado (vacío = todos).",
    )

    @api.depends()
    def _compute_allowed_for_user(self):
        allowed_ids = self.env.user.account_journal_ids.ids
        all_allowed = not bool(allowed_ids)
        for journal in self:
            journal.allowed_for_user = all_allowed or (journal.id in allowed_ids)
