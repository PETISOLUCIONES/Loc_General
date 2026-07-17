# -*- coding: utf-8 -*-

import logging
from markupsafe import Markup, escape
from odoo import _, api, exceptions, fields, models, tools, SUPERUSER_ID, Command

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_post(self, *,
                     body='', subject=None, message_type='notification',
                     email_from=None, author_id=None, parent_id=False,
                     subtype_xmlid=None, subtype_id=False, partner_ids=None,
                     attachments=None, attachment_ids=None, body_is_html=False,
                     timestamp=None, **kwargs):

        self.ensure_one()  # should always be posted on a record, use message_notify if no record

        # preliminary value safety check
        self._raise_for_invalid_parameters(
            set(kwargs.keys()),
            forbidden_names={'model', 'res_id', 'subtype'}
        )
        if self._name == 'mail.thread' or not self.id:
            raise ValueError(
                _("Posting a message should be done on a business document. Use message_notify to send a notification to an user."))
        if message_type == 'user_notification':
            raise ValueError(_("Use message_notify to send a notification to an user."))
        if attachments:
            # attachments should be a list (or tuples) of 3-elements list (or tuple)
            format_error = not tools.is_list_of(attachments, list) and not tools.is_list_of(attachments, tuple)
            if not format_error:
                format_error = not all(len(attachment) in {2, 3} for attachment in attachments)
            if format_error:
                raise ValueError(
                    _('Posting a message should receive attachments as a list of list or tuples (received %(aids)s)',
                      aids=repr(attachment_ids),
                      )
                )
        if attachment_ids and not tools.is_list_of(attachment_ids, int):
            raise ValueError(
                _('Posting a message should receive attachments records as a list of IDs (received %(aids)s)',
                  aids=repr(attachment_ids),
                  )
            )
        attachment_ids = list(attachment_ids or [])
        if partner_ids and not tools.is_list_of(partner_ids, int):
            raise ValueError(
                _('Posting a message should receive partners as a list of IDs (received %(pids)s)',
                  pids=repr(partner_ids),
                  )
            )
        partner_ids = list(partner_ids or [])

        # split message additional values from notify additional values
        msg_kwargs = {key: val for key, val in kwargs.items() if key in self.env['mail.message']._fields}
        notif_kwargs = {key: val for key, val in kwargs.items() if key not in msg_kwargs}

        # Add lang to context immediately since it will be useful in various flows later
        self = self._fallback_lang()

        # Find the message's author
        guest = self.env['mail.guest']._get_guest_from_context()
        if self.env.user._is_public() and guest:
            author_guest_id = guest.id
            author_id, email_from = False, False
        else:
            author_guest_id = False
            author_id, email_from = self._message_compute_author(author_id, email_from, raise_on_email=True)

        if subtype_xmlid:
            subtype_id = self.env['ir.model.data']._xmlid_to_res_id(subtype_xmlid)
        if not subtype_id:
            subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        # automatically subscribe recipients if asked to
        if self._context.get('mail_post_autofollow') and partner_ids:
            self.message_subscribe(partner_ids=list(partner_ids))

        msg_values = dict(msg_kwargs)
        if 'email_add_signature' not in msg_values:
            msg_values['email_add_signature'] = True
        if not msg_values.get('record_name'):
            # use sudo as record access is not always granted (notably when replying
            # a notification) -> final check is done at message creation level
            msg_values['record_name'] = self.sudo().display_name
        if body_is_html and self.user_has_groups("base.group_user"):
            _logger.warning("Posting HTML message using body_is_html=True, use a Markup object instead (user: %s)", self.env.user.id)
            body = Markup(body)
        msg_values.update({
            # author
            'author_id': author_id,
            'author_guest_id': author_guest_id,
            'email_from': email_from,
            # document
            'model': self._name,
            'res_id': self.id,
            # content
            'body': escape(body),  # escape if text, keep if markup
            'message_type': message_type,
            'parent_id': self._message_compute_parent_id(parent_id),
            'subject': subject or False,
            'subtype_id': subtype_id,
            # recipients
            'partner_ids': partner_ids,
            # time
            'timestamp': timestamp,
        })
        _logger.info('[whatsapp_extended/models/mail_thread.py]')
        _logger.info('timestamp: %s', timestamp)

        # add default-like values afterwards, to avoid useless queries
        if 'record_alias_domain_id' not in msg_values:
            msg_values['record_alias_domain_id'] = self.sudo()._mail_get_alias_domains(default_company=self.env.company)[self.id].id
        if 'record_company_id' not in msg_values:
            msg_values['record_company_id'] = self._mail_get_companies(default=self.env.company)[self.id].id
        if 'reply_to' not in msg_values:
            msg_values['reply_to'] = self._notify_get_reply_to(default=email_from)[self.id]

        msg_values.update(
            self._process_attachments_for_post(attachments, attachment_ids, msg_values)
        )  # attachement_ids, body
        new_message = self._message_create([msg_values])

        # subscribe author(s) so that they receive answers; do it only when it is
        # a manual post by the author (aka not a system notification, not a message
        # posted 'in behalf of', and if still active).
        author_subscribe = (not self._context.get('mail_create_nosubscribe') and msg_values['message_type'] != 'notification')
        if author_subscribe:
            real_author_id = False
            # if current user is active, they are the one doing the action and should
            # be notified of answers. If they are inactive they are posting on behalf
            # of someone else (a custom, mailgateway, ...) and the real author is the
            # message author
            if self.env.user.active:
                real_author_id = self.env.user.partner_id.id
            elif msg_values['author_id']:
                author = self.env['res.partner'].browse(msg_values['author_id'])
                if author.active:
                    real_author_id = author.id
            if real_author_id:
                self._message_subscribe(partner_ids=[real_author_id])

        self._message_post_after_hook(new_message, msg_values)
        self._notify_thread(new_message, msg_values, **notif_kwargs)
        return new_message

    def _get_message_create_valid_field_names(self):
        res = super(MailThread, self)._get_message_create_valid_field_names()
        res.add('timestamp')
        return res