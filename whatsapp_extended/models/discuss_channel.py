# -*- coding: utf-8 -*-

import logging
from datetime import date, datetime, timedelta
from markupsafe import Markup
from odoo import api, Command, fields, models, tools, _
from odoo.addons.whatsapp.tools import phone_validation as wa_phone_validation

_logger = logging.getLogger(__name__)


class ChatbotDiscussChannel(models.Model):
    _inherit = "discuss.channel"

    state = fields.Selection(
        selection=[
            ("open", "Abierto"),
            ("expired", "Expirado"),
        ],
        string="Estado",
        required=False,
        readonly=False,
        default="open",
    )

    def close_expired_channels(self):
        channels = self.search([])
        for channel in channels:
            if channel.whatsapp_channel_valid_until:
                if channel.whatsapp_channel_valid_until < datetime.now():
                    channel.state = 'expired'

    def _get_whatsapp_channel(self, whatsapp_number, wa_account_id, sender_name=False, create_if_not_found=False, related_message=False, default_channel=False):
        """ Crea un canal de WhatsApp.

        :param str whatsapp_number: Número de teléfono de WhatsApp del cliente. Debe estar
        formateado según los estándares de WhatsApp, es decir, {código_de_país}{número_nacional}.

        :returns: discusión de WhatsApp discuss.channel
        """

        # Ser precavido con el número, ya que se utiliza en varios flujos posteriores,
        # en particular en 'message_post' para el número, y es llamado por '_process_messages'.
        base_number = whatsapp_number if whatsapp_number.startswith('+') else f'+{whatsapp_number}'
        wa_number = base_number.lstrip('+')
        wa_formatted = wa_phone_validation.wa_phone_format(
            self.env.company,
            number=base_number,
            force_format="WHATSAPP",
            raise_exception=False,
        ) or wa_number

        related_record = False
        responsible_partners = self.env['res.partner']
        channel_domain = [
            ('whatsapp_number', '=', wa_formatted),
            ('wa_account_id', '=', wa_account_id.id)
        ]

        if related_message and not default_channel:
            related_record = self.env[related_message.model].browse(related_message.res_id)
            responsible_partners = related_record._whatsapp_get_responsible(
                related_message=related_message,
                related_record=related_record,
                whatsapp_account=wa_account_id,
            ).partner_id

            if 'message_ids' in related_record:
                record_messages = related_record.message_ids
            else:
                record_messages = self.env['mail.message'].search([
                    ('model', '=', related_record._name),
                    ('res_id', '=', related_record.id),
                    ('message_type', '!=', 'user_notification'),
                ])
            channel_domain += [
                ('whatsapp_mail_message_id', 'in', record_messages.ids),
            ]

        if default_channel:
            channel_domain += [
                ('name', '=', wa_formatted),
            ]

        channel = self.sudo().search(channel_domain, order='create_date desc', limit=1)
        if bool(responsible_partners):
            channel = channel.filtered(lambda c: all(r in c.channel_member_ids.partner_id for r in responsible_partners))

        partners_to_notify = responsible_partners
        record_name = related_message.record_name if bool(related_message) else False
        res_id = related_message.res_id if bool(related_message) else False

        if bool(not record_name and res_id):
            record_name = self.env[related_message.model].browse(res_id).display_name

        if bool(not channel and create_if_not_found):
            channel = self.sudo().with_context(tools.clean_context(self.env.context)).create({
                'name': f"{wa_formatted} ({record_name})" if record_name else wa_formatted,
                'channel_type': 'whatsapp',
                'whatsapp_number': wa_formatted,
                'whatsapp_partner_id': self.env['res.partner']._find_or_create_from_number(wa_formatted, sender_name).id,
                'wa_account_id': wa_account_id.id,
                'whatsapp_mail_message_id': related_message.id if related_message else None,
            })
            partners_to_notify += channel.whatsapp_partner_id
            if related_message:
                # Add message in channel about the related document
                info = _("%(model_name)s relacionado:", model_name=self.env['ir.model']._get(related_message.model).display_name)
                url = Markup('{base_url}/web#model={model}&id={res_id}').format(base_url=self.get_base_url(), model=related_message.model, res_id=res_id)
                related_record_name = related_message.record_name
                if not related_record_name:
                    related_record_name = self.env[related_message.model].browse(res_id).display_name
                channel.message_post(
                    body=Markup('<p>{info} <a target="_blank" href="{url}">{related_record_name}</a></p>').format(info=info, url=url, related_record_name=related_record_name),
                    message_type='comment',
                    author_id=self.env.ref('base.partner_root').id,
                    subtype_xmlid='mail.mt_note',
                )
                if hasattr(related_record, 'message_post'):
                    # Add notification in document about the new message and related channel
                    info = _("Se ha creado un nuevo canal de WhatsApp para este documento:")
                    url = Markup('{base_url}/web#model=discuss.channel&id={channel_id}').format(base_url=self.get_base_url(), channel_id=channel.id)
                    related_record.message_post(
                        author_id=self.env.ref('base.partner_root').id,
                        body=Markup('<p>{info} <a target="_blank" class="o_whatsapp_channel_redirect" data-oe-id="{channel_id}" href="{url}">{channel_name}</a></p>').format(info=info, url=url, channel_id=channel.id, channel_name=channel.display_name),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note',
                    )

            if partners_to_notify == channel.whatsapp_partner_id and wa_account_id.notify_user_ids.partner_id:
                partners_to_notify += wa_account_id.notify_user_ids.partner_id

            # Asegurar que no se repitan miembros
            partners_to_notify = partners_to_notify | partners_to_notify

            channel.channel_member_ids = [Command.clear()] + [Command.create({'partner_id': partner.id}) for partner in partners_to_notify]
            channel._broadcast(partners_to_notify.ids)

        return channel
