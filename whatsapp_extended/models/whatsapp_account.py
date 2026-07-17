# -*- coding: utf-8 -*-

import logging
import mimetypes
import threading
import requests
import json
import urllib.request
import base64

from markupsafe import Markup
from odoo import Command, _, models, fields
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.addons.whatsapp.tools.whatsapp_exception import WhatsAppError
from odoo.addons.whatsapp.tools.whatsapp_api import WhatsAppApi
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://graph.facebook.com/v17.0/"


class WhatsappAccount(models.Model):
    _inherit = 'whatsapp.account'

    about = fields.Text("About", readonly=True)
    business_address = fields.Text("Address", readonly=True)
    business_description = fields.Text("Description", readonly=True)
    business_email = fields.Char("Email", readonly=True)
    business_profile_picture = fields.Image("Profile Picture", readonly=True, attachment=True, copy=False)
    business_website = fields.Char("Website", readonly=True)
    business_vertical = fields.Char("Vertical", readonly=True)

    verified_name = fields.Char("Verified Name", readonly=True)
    code_verification_status = fields.Char("Code Verification Status", readonly=True)
    display_phone_number = fields.Char("Display Phone Number", readonly=True)
    quality_rating = fields.Char("Quality Rating", readonly=True)
    platform_type = fields.Char("Platform Type", readonly=True)
    throughput_level = fields.Char("Throughput Level", readonly=True)
    webhook_configuration = fields.Char("Webhook Configuration", readonly=True)

    def _prepare_error_response_ext(self, response):
        """
        This method is used to prepare error response
        :return tuple[str, int]: (error_message, whatsapp_error_code | -1)
        """
        if response.get("error"):
            error = response["error"]
            desc = error.get("message", "")
            desc += (
                (" - " + error["error_user_title"])
                if error.get("error_user_title")
                else ""
            )
            desc += (
                ("\n\n" + error["error_user_msg"])
                if error.get("error_user_msg")
                else ""
            )
            code = error.get("code", "odoo")
            return (desc if desc else _("Non-descript Error"), code)
        return (
            _(
                "Something went wrong when contacting WhatsApp, please try again later. If this happens frequently, contact support."
            ),
            -1,
        )

    def _api_requests_ext(
            self,
            request_type,
            url,
            auth_type="",
            params=False,
            headers=None,
            data=False,
            files=False,
            endpoint_include=False,
    ):
        if getattr(threading.current_thread(), "testing", False):
            raise WhatsAppError("API requests disabled in testing.")

        headers = headers or {}
        params = params or {}
        if not all([self.token, self.phone_uid]):
            action = self.env.ref("whatsapp.whatsapp_account_action")
            raise RedirectWarning(
                _("To use WhatsApp Configure it first"),
                action=action.id,
                button_text=_("Configure Whatsapp Business Account"),
            )
        if auth_type == "oauth":
            headers.update({"Authorization": f"OAuth {self.token}"})
        if auth_type == "bearer":
            headers.update({"Authorization": f"Bearer {self.token}"})
        call_url = (DEFAULT_ENDPOINT + url) if not endpoint_include else url

        try:
            res = requests.request(
                request_type,
                call_url,
                params=params,
                headers=headers,
                data=data,
                files=files,
                timeout=10,
            )
        except requests.exceptions.RequestException:
            raise WhatsAppError(failure_type="network")

        # raise if json-parseable and 'error' in json
        try:
            if "error" in res.json():
                raise WhatsAppError(
                    *self._prepare_error_response_ext(res.json())
                )
        except ValueError:
            if not res.ok:
                raise WhatsAppError(failure_type="network")

        return res

    def get_whatsapp_business_details(self):
        if DEFAULT_ENDPOINT and self.phone_uid and self.token:
            url = DEFAULT_ENDPOINT + self.phone_uid + '/whatsapp_business_profile?fields=about,address,description,email,profile_picture_url,websites,vertical'
            data = {}
            headers = {
                'Authorization': 'Bearer ' + self.token
            }
            try:
                response = requests.get(url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            try:
                if response.status_code == 200:
                    dict = json.loads(response.text)
                    for data in dict.get('data'):
                        profile_picture_url = data.get('profile_picture_url')
                        self.about = data.get('about', '')
                        self.business_address = data.get('address', '')
                        self.business_description = data.get('description', '')
                        self.business_email = data.get('email', '')
                        self.business_website = data.get('websites', '')
                        self.business_vertical = data.get('vertical', '')
                        if profile_picture_url:
                            business_profile_picture = urllib.request.urlopen(profile_picture_url).read()
                            self.business_profile_picture = base64.b64encode(business_profile_picture)
            except Exception as e:
                raise ValidationError(e)
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def get_phone_number_by_id(self):
        if DEFAULT_ENDPOINT and self.phone_uid and self.token:
            url = DEFAULT_ENDPOINT + self.phone_uid
            data = {}
            headers = {
                'Authorization': 'Bearer ' + self.token
            }
            try:
                response = requests.get(url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            try:
                if response.status_code == 200:
                    data = json.loads(response.text)
                    if data:
                        self.verified_name = data.get('verified_name', '')
                        self.code_verification_status = data.get('code_verification_status', '')
                        self.display_phone_number = data.get('display_phone_number', '')
                        self.quality_rating = data.get('quality_rating', '')
                        self.platform_type = data.get('platform_type', '')
                        self.throughput_level = data.get('throughput').get('level') if data.get(
                            'throughput') and data.get('throughput').get('level') else ''
                        self.webhook_configuration = data.get('webhook_configuration').get('application') if data.get(
                            'webhook_configuration') and data.get('webhook_configuration').get('application') else ''
            except Exception as e:
                raise ValidationError(e)
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def _process_messages(self, value):
        """
            This method is used for processing messages with the values received via webhook.
            If any whatsapp message template has been sent from this account then it will find the active channel or
            create new channel with last template message sent to that number and post message in that channel.
            And if channel is not found then it will create new channel with notify user set in account and post message.
            Supported Messages
             => Text Message
             => Attachment Message with caption
             => Location Message
             => Contact Message
             => Message Reactions
        """
        if 'messages' not in value and value.get('whatsapp_business_api_data', {}).get('messages'):
            value = value['whatsapp_business_api_data']

        wa_api = WhatsAppApi(self)

        for messages in value.get('messages', []):
            parent_id = False
            channel = False
            sender_name = value.get('contacts', [{}])[0].get('profile', {}).get('name')
            sender_mobile = messages['from']
            message_type = messages['type']
            if 'context' in messages and messages['context'].get('id'):
                parent_whatsapp_message = self.env['whatsapp.message'].sudo().search([('msg_uid', '=', messages['context']['id'])])
                if parent_whatsapp_message:
                    parent_id = parent_whatsapp_message.mail_message_id
                if parent_id:
                    channel = self.env['discuss.channel'].sudo().search([('message_ids', 'in', parent_id.id)], limit=1)

            if not channel:
                channel = self._find_active_channel(sender_mobile, sender_name=sender_name, create_if_not_found=True)

            kwargs = {
                'message_type': 'whatsapp_message',
                'author_id': channel.whatsapp_partner_id.id,
                'subtype_xmlid': 'mail.mt_comment',
                'parent_id': parent_id.id if parent_id else None,
                'timestamp': messages['timestamp']
            }

            _logger.info('[whatsapp_extended/models/whatsapp_account.py]')
            _logger.info('timestamp: %s', messages['timestamp'])

            if message_type == 'text':
                kwargs['body'] = plaintext2html(messages['text']['body'])

            elif message_type == 'button':
                kwargs['body'] = messages['button']['text']

            elif message_type in ('document', 'image', 'audio', 'video', 'sticker'):
                filename = messages[message_type].get('filename')
                mime_type = messages[message_type].get('mime_type')
                caption = messages[message_type].get('caption')
                datas = wa_api._get_whatsapp_document(messages[message_type]['id'])
                if not filename:
                    extension = mimetypes.guess_extension(mime_type) or ''
                    filename = message_type + extension
                kwargs['attachments'] = [(filename, datas)]
                if caption:
                    kwargs['body'] = plaintext2html(caption)

            elif message_type == 'location':
                url = Markup("https://maps.google.com/maps?q={latitude},{longitude}").format(latitude=messages['location']['latitude'], longitude=messages['location']['longitude'])
                body = Markup('<a target="_blank" href="{url}"> <i class="fa fa-map-marker"/> {location_string} </a>').format(url=url, location_string=_("Location"))
                if messages['location'].get('name'):
                    body += Markup("<br/>{location_name}").format(location_name=messages['location']['name'])
                if messages['location'].get('address'):
                    body += Markup("<br/>{location_address}").format(location_name=messages['location']['address'])
                kwargs['body'] = body

            elif message_type == 'contacts':
                body = ""
                for contact in messages['contacts']:
                    body += Markup("<i class='fa fa-address-book'/> {contact_name} <br/>").format(contact_name=contact.get('name', {}).get('formatted_name', ''))
                    for phone in contact.get('phones'):
                        body += Markup("{phone_type}: {phone_number}<br/>").format(phone_type=phone.get('type'), phone_number=phone.get('phone'))
                kwargs['body'] = body

            elif message_type == 'reaction':
                msg_uid = messages['reaction'].get('message_id')
                whatsapp_message = self.env['whatsapp.message'].sudo().search([('msg_uid', '=', msg_uid)])
                if whatsapp_message:
                    partner_id = channel.whatsapp_partner_id
                    emoji = messages['reaction'].get('emoji')
                    whatsapp_message.mail_message_id._post_whatsapp_reaction(reaction_content=emoji, partner_id=partner_id)
                    continue

            else:
                _logger.warning("Unsupported whatsapp message type: %s", messages)
                continue

            channel.message_post(whatsapp_inbound_msg_uid=messages['id'], **kwargs)
