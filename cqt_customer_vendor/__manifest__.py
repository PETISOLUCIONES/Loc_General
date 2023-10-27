# -*- coding: utf-8 -*-
{
    'name': "Is Customer Is Vendor in Odoo15",
    'version': '15.0.0.0.1',
    'description': "Using this module user can access Is customer/vendor as per Odoo Old versions in Odoo 15",
    'author': 'Cronquotech',
    'support': 'cronquotech@gmail.com',
    'website': "https://cronquotech.odoo.com",
    'summary': 'Is Customer Is Vendor,'
               'Partner,'
               'Customer,'
               'Vendor,'
               'Supplier,'
               'customer field, Odoo, Sales, Contacts'
    ,
    'category': 'Tools',
    'depends': ['base', 'sale_management', 'purchase'],
    'data': [
        'views/res_partner_view.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml'
    ],
    'images': [
        'static/description/banner.png',
    ],
    'post_init_hook': 'update_old_contacts',
    'price': 5.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: