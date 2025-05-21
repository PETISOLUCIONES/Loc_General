# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying the sale order.",
        default=9999,
    )

    visible_sequence = fields.Integer(
        "Line Number",
        help="Displays the sequence of the line in the sale order.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._ordenar_lineas()
        return lines

    def _ordenar_lineas(self):
        orders = self.mapped("order_id")
        for order in orders:
            sequence = 1
            # Filtrar solo líneas normales (no display_type)
            order_lines = order.order_line.filtered(lambda l: not l.display_type)
            # Ordenar por 'sequence'
            for line in sorted(order_lines, key=lambda l: l.sequence):
                line.visible_sequence = sequence
                sequence += 1
