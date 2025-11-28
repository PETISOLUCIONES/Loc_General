# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Inventory Barcode Scanning",
  "summary"              :  """The module allows you to scan the product barcode and update the quantity of stock in Odoo inventory.""",
  "category"             :  "Warehouse",
  "version"              :  "1.0.3",
  "sequence"             :  "10",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Inventory-Barcode-Scanning.html",
  "description"          :  """Odoo Inventory Barcode Scanning
Odoo advanced barcode scanning
Scan products with barcode
Add product to inventory
Odoo Scan products to stock in Odoo
Scan barcode in Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=barcode_stock",
  "depends"              :  ['stock', 'stock_picking_batch'],
  "data"                 :  [
        'views/stock_picking_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_batch_views.xml',
    ],
  "assets"               :  {
        'web.assets_backend': [
            'barcode_stock/static/src/barcode_list_controller.js',
        ],
    },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "price"                :  15,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
