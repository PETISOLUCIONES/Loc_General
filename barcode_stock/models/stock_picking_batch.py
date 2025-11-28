# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, models
from odoo.exceptions import UserError


class StockPickingBatch(models.Model):
    _name = 'stock.picking.batch'
    _inherit = ['stock.picking.batch', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search(
            ['|',('barcode', '=', barcode),('default_code', '=', barcode)]
            , limit=1)
        if product:
            moveLineObjs = self.move_line_ids.filtered(
                lambda r: r.product_id == product)

            if moveLineObjs:
                # Resetear last_scanned de todas las líneas del batch
                self.move_line_ids.write({'last_scanned': False})

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
            else:
                raise UserError(
                    _('This product %s with barcode %s is not present in this batch.') %
                    (product.name, barcode))
        else:
            raise UserError(
                _('This barcode %s is not related to any product.') %
                barcode)