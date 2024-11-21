# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class VendorRegisterRejectReason(models.TransientModel):
	_name = 'wizard.vendor.register.reject.reason'
	_description="reject reason description"

	reason = fields.Char('Reject Reason', required=True)
	name = fields.Char(string="Name")
	vendor_req_id = fields.Many2one('vendor.registration.request', string="Vendor request")

	@api.model
	def default_get(self, fields):
		res = super(VendorRegisterRejectReason, self).default_get(fields)
		active_id = self.env.context.get('active_id')
		vendor_req_id = self.env['vendor.registration.request'].browse(active_id)
		if 'name' in fields:
			res.update({'name': vendor_req_id.name})
		res.update({'vendor_req_id': vendor_req_id.id})
		return res
	
	def confirm(self):
		vendor_req_id = self.env['vendor.registration.request'].browse(int(self._context.get('active_id')))
		vendor_req_id.update({'state': 'reject'})
		template_id = self.env.ref('bi_vendor_registration_request.reject_reason_email_template').id
		template = self.env['mail.template'].browse(template_id)
		template.send_mail(self.id, force_send=True)

	def cancel(self):
		return True
