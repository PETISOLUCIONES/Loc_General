# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    allowed_journal = fields.Boolean(
        string="Permitido para el usuario",
        compute="_compute_allowed_journal",
        # precompute=True,
        # store=True,
        # readonly=True,
        # index=True,
        help="True si el diario NO está en los permitidos para el usuario o si el usuario no tiene ninguno configurado (vacío = todos).",
    )

    @api.depends('journal_id')
    def _compute_allowed_journal(self):
        allowed_ids = self.env.user.account_journal_ids.ids
        all_allowed = not bool(allowed_ids)
        for move in self:
            move.allowed_journal =  all_allowed or move.journal_id.id not in allowed_ids

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        allowed = self.env.user.account_journal_ids.ids
        for move in self:
            if move.journal_id.id not in allowed:
                move.journal_id = False

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields=allfields, attributes=attributes)
        enable_journals_per_user = self.env.user.company_id.enable_journals_per_user
        has_group = self.env.user.has_group('account_authorized_journal.group_journal_limits')
        if enable_journals_per_user and has_group and 'journal_id' in res:
            allowed = self.env.user.account_journal_ids.ids
            if allowed:
                extra = f"('id','in',{allowed})"
                existing = res['journal_id'].get('domain')
                if existing:
                    body = existing[1:-1]
                    res['journal_id']['domain'] = f"[({body}), {extra}]"
                else:
                    res['journal_id']['domain'] = f"[{extra}]"
        return res

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        enable_journals_per_user = self.env.user.company_id.enable_journals_per_user
        has_group = self.env.user.has_group('account_authorized_journal.group_journal_limits')
        if enable_journals_per_user and has_group and view_type in ('form', 'tree'):
            allowed = self.env.user.account_journal_ids.ids
            if allowed:
                extra = f"('id','in',{allowed})"
                for node in arch.xpath("//field[@name='journal_id']"):
                    existing = node.get('domain')
                    if existing:
                        body = existing[1:-1]
                        node.set('domain', f"[({body}), {extra}]")
                    else:
                        node.set('domain', f"[{extra}]")
        return arch, view
