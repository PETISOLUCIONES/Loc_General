# -*- coding: utf-8 -*-

import json
import logging
import threading

import markupsafe
import requests

from odoo import Command, _, models, fields
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import groupby

from odoo.addons.whatsapp.tools.whatsapp_api import WhatsAppApi
from odoo.addons.whatsapp.tools.whatsapp_exception import WhatsAppError

_logger = logging.getLogger(__name__)
DEFAULT_ENDPOINT = "https://graph.facebook.com/v17.0"


class WhatsappMessage(models.Model):
    _inherit = "whatsapp.message"

    def _send_whatsapp_ext(self, number, message_type, send_vals, parent_message_id=False):
        """
        Enviar mensajes de WhatsApp para todo tipo de mensajes usando la cuenta de WhatsApp Business

        Documentación API:
            Normal           - https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages
            Enviar plantilla - https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-message-templates
        """
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
        }

        # Si hay parent_message_id entonces enviamos mensaje como respuesta
        if parent_message_id:
            data.update({
                "context": {"message_id": parent_message_id},
            })

        if message_type in ("template", "text", "document", "image", "audio", "video", "interactive"):
            data.update({
                "type": message_type, message_type: send_vals
            })

        json_data = json.dumps(data)

        _logger.info("Enviar mensaje %s desde la cuenta %s [%s]", message_type, self.wa_account_id.name, self.wa_account_id.id)

        response = self.wa_account_id._api_requests_ext(
            "POST",
            f"/{self.wa_account_id.phone_uid}/messages",
            auth_type="bearer",
            headers={"Content-Type": "application/json"},
            data=json_data,
        )

        response_json = response.json()
        if response_json.get("messages"):
            msg_uid = response_json["messages"][0]["id"]
            return msg_uid

        raise WhatsAppError(*self.wa_account_id._prepare_error_response_ext(response_json))

    def _send_message(self, with_commit=False):
        """Preparar datos json para el envío de mensajes, archivos adjuntos y plantillas."""
        message_to_api = {}
        for account, messages in groupby(self, lambda msg: msg.wa_account_id):
            if not account:
                messages = self.env["whatsapp.message"].concat(*messages)
                messages.write({
                    "failure_type": "unknown",
                    "failure_reason": "Missing whatsapp account for message.",
                    "state": "error",
                })
                self -= messages
                continue

            wa_api = WhatsAppApi(account)
            for message in messages:
                message_to_api[message] = wa_api

        for whatsapp_message in self:
            whatsapp_message = whatsapp_message.with_user(whatsapp_message.create_uid)
            try:
                parent_message_id = False
                body = whatsapp_message.body
                if isinstance(body, markupsafe.Markup):
                    # Si el cuerpo está en formato html, debemos eliminar las etiquetas html antes de enviar el mensaje.
                    body = body.striptags()

                number = whatsapp_message.mobile_number_formatted
                if not number:
                    raise WhatsAppError(failure_type="phone_invalid")

                if (self.env["phone.blacklist"].sudo().search([("number", "ilike", number)])):
                    raise WhatsAppError(failure_type="blacklisted")

                if (whatsapp_message.wa_template_id and whatsapp_message.wa_template_id.template_category == "interactive"):
                    message_type = "interactive"
                    if (whatsapp_message.wa_template_id.status != "approved" or whatsapp_message.wa_template_id.quality in ("red", "yellow")):
                        raise WhatsAppError(failure_type="template")

                    whatsapp_message.message_type = "outbound"
                    if (whatsapp_message.mail_message_id.model != whatsapp_message.wa_template_id.model):
                        raise WhatsAppError(failure_type="template")

                    RecordModel = self.env[whatsapp_message.mail_message_id.model].with_user(whatsapp_message.create_uid)
                    from_record = RecordModel.browse(whatsapp_message.mail_message_id.res_id)
                    (send_vals, attachment) = whatsapp_message.wa_template_id._get_send_template_vals(record=from_record, free_text_json=whatsapp_message.free_text_json, attachment=whatsapp_message.mail_message_id.attachment_ids)
                    if attachment:
                        # Si se reintenta el mensaje, hay que eliminar el archivo adjunto anterior y añadir uno nuevo.
                        if (whatsapp_message.mail_message_id.attachment_ids and whatsapp_message.wa_template_id.header_type == "document" and whatsapp_message.wa_template_id.report_id):
                            whatsapp_message.mail_message_id.attachment_ids.unlink()
                        if (attachment not in whatsapp_message.mail_message_id.attachment_ids):
                            whatsapp_message.mail_message_id.attachment_ids = [Command.link(attachment.id)]
                else:
                    return super(WhatsappMessage, self)._send_message(with_commit=False)

                msg_uid = whatsapp_message._send_whatsapp_ext(number=number, message_type=message_type, send_vals=send_vals, parent_message_id=parent_message_id)

            except WhatsAppError as we:
                whatsapp_message._handle_error(whatsapp_error_code=we.error_code, error_message=we.error_message, failure_type=we.failure_type)

            except (UserError, ValidationError) as e:
                whatsapp_message._handle_error(failure_type="unknown", error_message=str(e))

            else:
                if not msg_uid:
                    whatsapp_message._handle_error(failure_type="unknown")
                else:
                    if message_type == "interactive":
                        whatsapp_message._post_message_in_active_channel()
                    whatsapp_message.write({"state": "sent", "msg_uid": msg_uid})
                if with_commit:
                    self._cr.commit()
