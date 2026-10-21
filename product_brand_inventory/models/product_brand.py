# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models


class ProductBrand(models.Model):
    """Inherit product brand to add inventory features and compatibility"""
    _inherit = 'product.brand'

    brand_image = fields.Binary(
        string="Brand Image",
        related='logo',
        readonly=False,
        help="Brand image of product"
    )
    member_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string="Products",
        help="Number of Products"
    )
    product_count = fields.Integer(
        string='Product Count',
        help="Number of products",
        compute='_compute_product_count',
        store=False
    )

    @api.depends('member_ids')
    def _compute_product_count(self):
        """Compute number of products in product brand"""
        for brand in self:
            brand.product_count = len(brand.member_ids)
