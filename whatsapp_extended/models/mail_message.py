# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import _, api, Command, fields, models, modules, tools

_logger = logging.getLogger(__name__)


class Message(models.Model):
    _inherit = 'mail.message'

    timestamp = fields.Integer(
        string='Timestamp',
        help='Timestamp of the message',
        required=False,
        readonly=False,
    )

    real_date = fields.Datetime(
        string='Real Date',
        help='Real date of the message',
        compute='_compute_real_date',
        store=True,
        readonly=False,
    )

    @api.depends('timestamp')
    def _compute_real_date(self):
        for record in self:
            if record.timestamp:
                # Conversión de unit timestamp a datetime
                # record.real_date = datetime.datetime.utcfromtimestamp(record.timestamp)
                record.real_date = datetime.datetime.fromtimestamp(record.timestamp)
                _logger.info('[whatsapp_extended/models/mail_message.py]')
                _logger.info('timestamp: %s', record.timestamp)
                _logger.info('real_date: %s', record.real_date)
            else:
                record.real_date = False
                _logger.info('[whatsapp_extended/models/mail_message.py]')
                _logger.info('Dont have timestamp')
