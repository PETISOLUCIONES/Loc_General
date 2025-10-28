from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_scanned = fields.Boolean(
        string='Scanned',
        compute='_compute_is_scanned',
        inverse='_set_is_scanned',
        store=True,
        help='Indica si este movimiento ha sido escaneado con el lector de código de barras'
    )

    last_scanned = fields.Boolean(
        string='Last Scanned',
        compute='_compute_last_scanned',
        inverse='_set_last_scanned',
        store=True,
        help='Indica si este movimiento fue el último en ser escaneado (para resaltado visual)'
    )

    @api.depends('move_line_ids.is_scanned')
    def _compute_is_scanned(self):
        """Computa is_scanned basándose en si alguna move line ha sido escaneada"""
        for move in self:
            move.is_scanned = any(move.move_line_ids.mapped('is_scanned'))

    def _set_is_scanned(self):
        """Propaga el valor de is_scanned a todas las move lines"""
        for move in self:
            if move.move_line_ids:
                move.move_line_ids.write({'is_scanned': move.is_scanned})

    @api.depends('move_line_ids.last_scanned')
    def _compute_last_scanned(self):
        """Computa last_scanned basándose en si alguna move line fue la última escaneada"""
        for move in self:
            move.last_scanned = any(move.move_line_ids.mapped('last_scanned'))

    def _set_last_scanned(self):
        """Propaga el valor de last_scanned a todas las move lines"""
        for move in self:
            if move.move_line_ids:
                move.move_line_ids.write({'last_scanned': move.last_scanned})
