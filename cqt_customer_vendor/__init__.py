# -*- coding: utf-8 -*-

from . import models

def update_old_contacts(cr, registry):
    # Update Customer
    cr.execute("UPDATE res_partner SET is_customer='t' where customer_rank > 0;")
    # Update Vendor
    cr.execute("UPDATE res_partner SET is_vendor='t' where supplier_rank > 0;")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: