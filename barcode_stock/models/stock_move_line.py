from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _name = 'stock.move.line'
    _inherit = 'stock.move.line'

    is_scanned = fields.Boolean(
        string='Scanned',
        default=False,
        help='Indica si esta línea ha sido escaneada con el lector de código de barras'
    )

    last_scanned = fields.Boolean(
        string='Last Scanned',
        default=False,
        help='Indica si esta línea fue la última en ser escaneada (para resaltado visual)'
    )

    @api.model
    def process_barcode_from_tree(self, line_ids, barcode):
        """
        Procesa un código de barras escaneado desde una vista tree.
        Este método replica EXACTAMENTE la lógica de stock.picking.on_barcode_scanned

        :param line_ids: Lista de IDs de las líneas visibles en la tree
        :param barcode: Código de barras escaneado
        """
        # Buscar el producto por código de barras o referencia interna
        product = self.env['product.product'].search(
            ['|', ('barcode', '=', barcode), ('default_code', '=', barcode)],
            limit=1
        )

        if not product:
            raise UserError(
                _('This barcode %s is not related to any product.') % barcode
            )

        # Obtener todas las líneas del recordset
        lines = self.browse(line_ids)

        if not lines:
            raise UserError(_('No lines found to process.'))

        # Obtener el picking (asumiendo que todas las líneas son del mismo picking)
        picking = lines[0].picking_id

        if not picking:
            raise UserError(_('Lines must belong to a picking.'))

        # Filtrar líneas del mismo producto en el picking
        moveLineObjs = picking.move_line_ids_without_package.filtered(
            lambda r: r.product_id == product
        )

        if not moveLineObjs:
            raise UserError(
                _('This product %s with barcode %s is not present in this picking.') %
                (product.name, barcode)
            )

        # Resetear last_scanned de TODAS las líneas del picking
        picking.move_line_ids_without_package.write({'last_scanned': False})

        # LÓGICA EXACTA DE stock.picking.on_barcode_scanned
        for moveLineObj in moveLineObjs:
            # Si no ha sido escaneado, inicializar quantity a 1 y marcar como escaneado
            if not moveLineObj.is_scanned:
                moveLineObj.quantity = 1
                moveLineObj.is_scanned = True
                moveLineObj.last_scanned = True
                break
            # Si ya fue escaneado, incrementar si no excede el límite
            elif moveLineObj.quantity < moveLineObj.move_id.product_uom_qty:
                moveLineObj.quantity += 1
                moveLineObj.last_scanned = True
                break
            elif moveLineObj == moveLineObjs[-1]:
                raise UserError(
                    _('⚠️ Cantidad excedida para:\n'
                      'Producto: %s\n'
                      'Cantidad ordenada: %s\n'
                      'Ubicación: %s') % (
                        moveLineObj.product_id.display_name,
                        moveLineObj.move_id.product_uom_qty,
                        moveLineObj.location_id.complete_name or moveLineObj.location_id.name
                    )
                )
