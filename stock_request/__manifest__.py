# -*- coding: utf-8 -*-
{
    "name": "Stock Request",
    "summary": "Internal request for stock",
    "version": "17.0.1.1.3",
    "license": "LGPL-3",
    "website": "http://www.peti.com.co",
    "author": "PETI Soluciones Productivas",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "security/stock_request_security.xml",
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/stock_request_views.xml",
        "views/stock_request_allocation_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_request_order_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_request_menu.xml",
        "data/stock_request_sequence_data.xml",
    ],
    "installable": True,
}
