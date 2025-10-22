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
                for moveLineObj in moveLineObjs:
                    if moveLineObj.quantity < moveLineObj.move_id.product_uom_qty:
                        moveLineObj.quantity += 1
                        break
                    elif moveLineObj == moveLineObjs[-1]:
                        raise UserError(
                            _('You are trying to deliver quantity more than ordered.'))
            elif moveObjs and operation_on=='move':
                for moveObj in moveObjs:
                    if moveObj.quantity < moveObj.product_uom_qty:
                        moveObj.quantity += 1
                        break
                    elif moveObj == moveObjs[-1]:
                        raise UserError(
                            _('You are trying to deliver quantity more than ordered.'))
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
