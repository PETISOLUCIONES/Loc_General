# -*- coding: utf-8 -*-
{
    "name": "Odoo WhatsApp Chatbot",
    "summary": "Odoo Whatsapp Chatbot Integration, Interactive Templates, Buttons send through odoo on WhatsApp and Message Automation",
    "description": """
        Odoo Whatsapp Chatbot Integration,
        Interactive Templates,
        Buttons send through odoo on WhatsApp and Message Automation
        Odoo Chatbot
        Chatbot
        Odoo
        ERP
        Odoo ERP
        WhatsApp
        Whats-App
        Discuss
        App
        Community
        Odoo Whatsapp Chatbot
        Whatsapp Chatbot
        Odoo V17 Enterprise Edition
    """,
    'author': "PETI Soluciones Productivas",
    'website': "http://peti.erp.com.co",
    'category': 'WhatsApp',
    'version': '19.0.1.0',
    'license': 'OPL-1',
    "depends": ["whatsapp_extended"],
    "data": [
        "security/ir.model.access.csv",
        # "data/wa_template.xml",
        # "data/whatsapp_chatbot.xml",
        "views/whatsapp_chatbot_script_views.xml",
        "views/discuss_channel_views.xml",
        "views/whatsapp_chatbot_views.xml",
        "views/whatsapp_ir_action_views.xml",
        "views/whatsapp_account_inherit_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/odoo_whatsapp_ent_chatbot/static/src/scss/kanban_view.scss"
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
