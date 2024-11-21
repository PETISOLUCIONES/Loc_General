# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

import werkzeug
import json
import base64

import odoo.http as http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class WebsiteVendorRegistration(CustomerPortal):

	@http.route(['/vendor_req'], type='http', auth="public", website=True,sitemap=False)
	def vendor_registration_req(self, **kw):
		name = ""
		if http.request.env.user.name != "Public user":
			name = http.request.env.user.name

		email = http.request.env.user.partner_id.email
		phone = http.request.env.user.partner_id.phone
		values = {'user_ids': name, 'email': email, 'phone': phone}

		return request.render("bi_vendor_registration_request.bi_vendor_registration_req", values)

	@http.route('/vendor_req/thankyou', type="http", auth="public", website=True,sitemap=False)
	def vendor_registration_req_thankyou(self, **post):
		if post.get('debug'):
			return request.render("bi_vendor_registration_request.bi_vendor_registration_thank_you")
		if post:
			country_id = request.env['res.country'].sudo().search([('id', '=', post.get('country_id'))])
			state_id = request.env['res.country.state'].sudo().search([('id', '=', post.get('state_id'))])
			vals = {
				'name': post['user_ids'],
				'email': post['email_from'],
				'phone': post['phone'],
				'mobile': post['mobile'],
				'street': post['street'],
				'city': post['city'],
				'zip': post['zipcode'],
				'link': post['link'],
				'country': country_id.id if country_id else None,
				'state_id': state_id.id if state_id else None,
				'state': 'to_approve',
				'types': post.get('type'),
			}
			vendor_req_obj = request.env['vendor.registration.request'].sudo().create(vals)
			if vendor_req_obj.types == 'company':
				child1_vals = {
					'name': post.get('child_ids1'),
					'email' : post.get('email_from1'),
					'phone' : post.get('phone1'),
				}
				vendor_req_obj.update({'child_ids': [(0, 0, child1_vals)]})
				child2_vals = {
					'name': post.get('child_ids2'),
					'email' : post.get('email_from2'),
					'phone' : post.get('phone2'),
				}
				vendor_req_obj.update({'child_ids': [(0, 0, child2_vals)]})
			file = request.httprequest.files.getlist('file')
			if file:
				for i in range(len(file)):
					vendor_req_obj.write({'vendor_image': base64.b64encode(file[i].read())})
		return request.render("bi_vendor_registration_request.bi_vendor_registration_thank_you")



	@http.route(['/my/state/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
	def country_info(self, country, **kw):
		return dict(
			fields=country.get_address_fields(),
			states=[(st.id, st.name, st.code) for st in country.get_website_sale_states()],
			phone_code=country.phone_code,
			zip_required=country.zip_required,
			state_required=country.state_required,
		)
