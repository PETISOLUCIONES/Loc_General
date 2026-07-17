# -*- coding: utf-8 -*-
{
    "name": "Whatsapp Extended",
    "summary": "Odoo Whatsapp Extended module is extended version of whatsapp enterprise",
    "description": """
        Whatsapp Extended,
        Interactive Templates,
        Odoo
        ERP
        Odoo ERP
        WhatsApp
        Whats-App
        Odoo V17 Enterprise Edition
    """,
    'author': "PETI Soluciones Productivas",
    'website': "http://peti.erp.com.co",
    'category': 'WhatsApp',
    'version': '19.0.1.0',
    'license': 'OPL-1',
    "depends": [
        "whatsapp",
        "base_automation",
        "mail"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/interactive_buttons_views.xml",
        "views/interactive_list_views.xml",
        "views/interactive_product_list_views.xml",
        "views/whatsapp_interactive_template_views.xml",
        "views/whatsapp_template_inherit_views.xml",
        "views/ir_actions.xml",
        "views/whatsapp_account_views.xml",
        "views/discuss_channel_views.xml",
        "tests/ir_cron.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'whatsapp_extended/static/src/xml/message.xml',
            'whatsapp_extended/static/src/xml/AgentsList.xml',
            'whatsapp_extended/static/src/js/agents/**/*',
            'whatsapp_extended/static/src/scss/*.scss',
            'whatsapp_extended/static/src/js/templates/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
