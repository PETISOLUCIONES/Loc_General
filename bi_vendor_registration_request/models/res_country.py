# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models

class ResCountry(models.Model):
	_inherit = 'res.country'

	def get_country_states(self):
		res = self.sudo().state_ids
		if mode == 'shipping':
			states = self.env['res.country.state']
			dom = ['|', ('country_ids', 'in', self.id), ('country_ids', '=', False), ('website_published', '=', True)]
			delivery_carriers = self.env['delivery.carrier'].sudo().search(dom)

			for carrier in delivery_carriers:
				if not carrier.country_ids or not carrier.state_ids:
					states = res
					break
				states |= carrier.state_ids
			res = res & states
		return res