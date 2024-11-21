# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendor Registration Portal',
    'version': '17.0.0.3',
    'category': 'Website',
    'summary': 'Website seller registration request on website vendor request portal vendor registration from website vendor signup portal vendor register request from web store seller register request from webshop seller request from marketplace vendor registration portal',
    'description': """

        Vendor Registration Portal Odoo App helps users to create vendor registration request through the website. Purchase manager can view all the request and they have access to approve or reject the vendor. When reject the vendor, Must be enter the rejection reason. Also user will get email notification for creation or rejection of vendor.

    """,
    'author': 'BrowseInfo',
    "price": 35,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_vendor_registration_request&version=17&edition=Community',
    'depends': ['base', 'portal', 'website','website_sale', 'purchase', 'contacts'],
    'data': [
        "data/email_template.xml",
        "security/ir.model.access.csv",
        "wizard/vendor_req_reject_form.xml",
        "views/vendor_req_form.xml",
        "views/vendor_reg_request_templates.xml",
    ],
     'assets': {
        'web.assets_frontend': [
            'bi_vendor_registration_request/static/src/js/front.js',
        ],
    },
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://www.browseinfo.com/demo-request?app=bi_vendor_registration_request&version=17&edition=Community',
    "images":['static/description/Vendor-Registration-Portal-Banner.gif'],
}
