# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search(
            ['|',('barcode', '=', barcode),('default_code', '=', barcode)]
            , limit=1)
        if product:
            moveLineObjs = self.move_line_ids_without_package.filtered(
                lambda r: r.product_id == product)
            moveObjs = self.move_ids_without_package.filtered(
                lambda r: r.product_id == product)
            operation_on = 'move_line'
            if not self.show_operations:
                operation_on = 'move'
            elif self.picking_type_code == 'incoming' and not self.show_reserved:
                raise UserError(
                    _('Please enable "Pre-fill Detailed Operations" or disable "Show Detailed Operations" in Operation Type "%s" for better scanning experiance https://prnt.sc/M3hSpW5XLWaF .'%(self.picking_type_id.display_name)))
            if moveLineObjs and operation_on=='move_line':
                # Resetear last_scanned de todas las líneas del picking
                self.move_line_ids_without_package.write({'last_scanned': False})

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
            elif moveObjs and operation_on=='move':
                # Resetear last_scanned de todos los movimientos del picking
                self.move_ids_without_package.write({'last_scanned': False})

                for moveObj in moveObjs:
                    # Si no ha sido escaneado, inicializar quantity a 1 y marcar como escaneado
                    if not moveObj.is_scanned:
                        moveObj.quantity = 1
                        moveObj.is_scanned = True
                        moveObj.last_scanned = True
                        break
                    # Si ya fue escaneado, incrementar si no excede el límite
                    elif moveObj.quantity < moveObj.product_uom_qty:
                        moveObj.quantity += 1
                        moveObj.last_scanned = True
                        break
                    elif moveObj == moveObjs[-1]:
                        raise UserError(
                            _('⚠️ Cantidad excedida para:\n'
                              'Producto: %s\n'
                              'Cantidad ordenada: %s\n'
                              'Ubicación: %s') % (
                                moveObj.product_id.display_name,
                                moveObj.product_uom_qty,
                                moveObj.location_id.complete_name or moveObj.location_id.name
                            )
                        )
            elif moveObjs:
                stateLabel = dict(
                    self.move_line_ids_without_package.fields_get('state')['state']['selection']).get(
                    moveObjs[0].state, '')
                raise UserError(
                    _('Scanned product %s with barcode %s is present in this picking but currently in "%s" state.') %
                    (product.display_name, barcode, stateLabel))
            else:
                raise UserError(
                    _('This product %s with barcode %s is not present in this picking.') %
                    (product.name, barcode))
        else:
            raise UserError(
                _('This barcode %s is not related to any product.') %
                barcode)
