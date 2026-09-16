# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

def post_init_hook(env):
    """
    Calcula y asigna la numeración correlativa a todas las líneas
    de órdenes de venta y alquileres existentes en la base de datos.
    """
    orders = env["sale.order"].search([])
    for order in orders:
        number = 1
        lines = order.order_line.filtered(lambda l: not l.display_type).sorted(
            key=lambda l: (l.sequence, l.id or 0)
        )
        for line in lines:
            line.visible_sequence = number
            number += 1
