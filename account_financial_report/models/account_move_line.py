# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).-
from collections import defaultdict

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account", compute="_compute_analytic_account_ids", store=True
    )

    @api.depends("analytic_distribution")
    def _compute_analytic_account_ids(self):
        # Prefetch all involved analytic accounts
        with_distribution = self.filtered("analytic_distribution")
        batch_by_analytic_account = defaultdict(list)
        analytic_distribution = {}
        for record in with_distribution:
            for key, value in record.analytic_distribution.items():
                # Si la clave contiene una coma, divídela en varios IDs
                if ',' in key:
                    ids = key.split(',')
                    for account_id in ids:
                        # Asigna el valor a cada id separado
                        analytic_distribution[int(account_id)] = value
                else:
                    # Si no contiene coma, usa la clave directamente
                    analytic_distribution[int(key)] = value
            for account_id in map(int, analytic_distribution):
                batch_by_analytic_account[account_id].append(record.id)
        existing_account_ids = set(
            self.env["account.analytic.account"]
            .browse(map(int, batch_by_analytic_account))
            .exists()
            .ids
        )
        # Store them
        self.analytic_account_ids = False
        for account_id, record_ids in batch_by_analytic_account.items():
            if account_id not in existing_account_ids:
                continue
            self.browse(record_ids).analytic_account_ids = [
                fields.Command.link(account_id)
            ]

    def init(self):
        cr = self._cr

        cr.execute("""
                   CREATE INDEX IF NOT EXISTS
                       aml_aged_report_idx
                       ON account_move_line(
                       company_id,
                       date,
                       account_id,
                       partner_id,
                       date_maturity
                       )
                   """)

        cr.execute("""
                   CREATE INDEX IF NOT EXISTS
                       aml_open_items_partial_idx
                       ON account_move_line(
                       company_id,
                       date,
                       account_id,
                       partner_id
                       )
                       WHERE amount_residual<>0
                   """)

        cr.execute("""
                   CREATE INDEX IF NOT EXISTS
                       am_state_idx
                       ON account_move(state)
                   """)

        cr.execute("ANALYZE account_move_line")


    @api.model
    def search_count(self, domain, limit=None):
        # In Big DataBase every time you change the domain widget this method
        # takes a lot of time. This improves performance
        if self.env.context.get("skip_search_count"):
            return 0
        return super().search_count(domain, limit=limit)
