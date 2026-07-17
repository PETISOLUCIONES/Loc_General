# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsappTemplate(models.Model):
    _inherit = "whatsapp.template"

    template_category = fields.Selection(
        selection=[
            ("template", "Template"),
            ("interactive", "Interactive")
        ],
        string="Tipo de plantilla",
    )
    wa_interactive_ids = fields.One2many(
        comodel_name="wa.interactive.template",
        inverse_name="wa_template_id",
        string="Interactive",
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Contact"
    )
    is_system_template = fields.Boolean(
        string="Es plantilla de sistema",
        default=False
    )

    @api.model
    def init(self):
        # Buscar cuenta de WhatsApp
        whatsapp_accounts = self.env['whatsapp.account'].search([('active', '=', True)])
        for whatsapp_account in whatsapp_accounts:
            try:
                # Probar conexión con WhatsApp
                whatsapp_account.button_test_connection()
                # Sincronizar detalles del negocio
                whatsapp_account.get_whatsapp_business_details()
                # Sincronizar números de teléfono
                whatsapp_account.get_phone_number_by_id()
                # Sincronizar plantillas de WhatsApp
                whatsapp_account.button_sync_whatsapp_account_templates()
            except:
                continue

    def _handle_existing_template(self, existing_template, vals):
        """
        Función auxiliar para manejar las actualizaciones de plantillas existentes.
        """
        if bool(existing_template.button_ids) and bool(vals.get('button_ids')):
            existing_template.button_ids.unlink()
        if bool(existing_template.variable_ids) and bool(vals.get('variable_ids')):
            existing_template.variable_ids.unlink()
        if bool(existing_template.header_attachment_ids) and bool(vals.get('header_attachment_ids')):
            existing_template.header_attachment_ids.unlink()
        if bool(existing_template.wa_interactive_ids) and bool(vals.get('wa_interactive_ids')):
            existing_template.wa_interactive_ids.unlink()

        existing_template.write(vals)
        return existing_template

    @api.model_create_multi
    def create(self, vals_list):
        """
        Crear plantillas de WhatsApp para todas las cuentas activas si no se proporciona una cuenta específica.
        """
        # Obtener todas las cuentas de WhatsApp activas
        whatsapp_accounts = self.env['whatsapp.account'].search([('active', '=', True)])

        interactive_templates = []
        non_interactive_templates = []
        existing_templates = self.env['whatsapp.template']
        new_templates = self.env['whatsapp.template']

        for vals in vals_list:
            if vals.get('wa_account_id'):
                # Verificar si la plantilla ya existe para la cuenta específica
                existing_template = self.env['whatsapp.template'].search([
                    '&',
                    '|',
                        ('template_name', '=', vals.get('template_name')),
                        ('name', '=', vals.get('name')),
                    ('wa_account_id', '=', vals.get('wa_account_id'))
                ], limit=1)

                if existing_template:
                    existing_templates += self._handle_existing_template(existing_template, vals)
                else:
                    if vals.get('wa_interactive_ids'):
                        interactive_templates.append(vals)
                    else:
                        non_interactive_templates.append(vals)
            else:
                # Si no se proporciona una cuenta de WhatsApp específica
                if not bool(whatsapp_accounts):
                    return super(WhatsappTemplate, self).create(vals_list)
                else:
                    for account in whatsapp_accounts:
                        # Verificar si la plantilla ya existe para la cuenta específica
                        existing_template = self.env['whatsapp.template'].search([
                            ('name', '=', vals.get('name')),
                            ('wa_account_id', '=', account.id)
                        ], limit=1)

                        if existing_template:
                            existing_templates += self._handle_existing_template(existing_template, vals)
                        else:
                            # Copiar los nuevos valores y asignar la cuenta de WhatsApp actual
                            new_vals = vals.copy()
                            new_vals['wa_account_id'] = account.id
                            if vals.get('wa_interactive_ids'):
                                interactive_templates.append(new_vals)
                            else:
                                non_interactive_templates.append(new_vals)

        # Crear los templates interactivos individualmente
        if interactive_templates:
            for template in interactive_templates:
                new_templates += super(WhatsappTemplate, self).create(template)

        # Crear los templates no interactivos todos juntos
        if non_interactive_templates:
            new_templates += super(WhatsappTemplate, self).create(non_interactive_templates)

        # Devolver las plantillas existentes y las plantillas recién creadas
        return existing_templates + new_templates

    def button_set_status_to_added(self):
        for rec in self:
            rec.status = "approved"

    def _get_interactive_component(self):
        params = []
        for interactive in self.wa_interactive_ids:
            template_dict = {}
            template_dict.update({"type": interactive.interactive_type})
            if self.header_type == "text":
                header = {"type": self.header_type, "text": self.header_text}
                template_dict.update({"header": header})
            elif self.header_type in ["image", "video", "document"]:
                attachment = self.header_attachment_ids
                header = [
                    self.env["whatsapp.message"]._prepare_attachment_vals(
                        attachment, wa_account_id=self.wa_account_id
                    )
                ]
                # if self.header_type == 'document':
                #     header[0].get(self.header_type).update({'filename': attachment.name})
                template_dict.update({"header": header[0]})
            if self.body:
                body = {"text": self.body}
                template_dict.update({"body": body})
            if self.footer_text:
                footer = {"text": self.footer_text}
                template_dict.update({"footer": footer})
            if interactive.interactive_type == "product_list":
                if interactive.interactive_product_list_ids:
                    section = []
                    for product in interactive.interactive_product_list_ids:
                        product_items = []

                        for products in product.product_list_ids:
                            product_item = {
                                "product_retailer_id": products.product_retailer_id
                            }

                            product_items.append(product_item)

                        section.append(
                            {
                                "title": product.main_title,
                                "product_items": product_items,
                            }
                        )

                    action = {"catalog_id": interactive.catalog_id, "sections": section}

                    template_dict.update({"action": action})

            elif interactive.interactive_type == "button":
                if interactive.interactive_button_ids:
                    buttons = []
                    for btn_id in interactive.interactive_button_ids:
                        buttons.append(
                            {
                                "type": "reply",
                                "reply": {"id": btn_id.id, "title": btn_id.title},
                            }
                        )
                    action = {"buttons": buttons}

                    template_dict.update({"action": action})

            elif interactive.interactive_type == "list":
                if interactive.interactive_list_ids:
                    section = []
                    for list_id in interactive.interactive_list_ids:
                        rows = []
                        for lists in list_id.title_ids:
                            title_ids = {
                                "id": lists.id,
                                "title": lists.title,
                                "description": lists.description or "",
                            }
                            rows.append(title_ids)

                        section.append({"title": list_id.main_title, "rows": rows})
                    action = {"button": list_id.main_title, "sections": section}
                    template_dict.update({"action": action})

            elif interactive.interactive_type == "product":
                action = {
                    "catalog_id": interactive.catalog_id,
                    "product_retailer_id": interactive.product_retailer_id,
                }
                template_dict.update({"action": action})

            if bool(template_dict):
                params.append(template_dict)
        return params

    def _get_send_template_vals(self, record, free_text_json, attachment=False):
        temp_vals = {}
        attachment = {}
        if self.template_category == "interactive":
            interactive = self._get_interactive_component()
            if interactive:
                temp_vals.update(interactive[0])
            return temp_vals, attachment
        else:
            return super(WhatsappTemplate, self)._get_send_template_vals(
                record, free_text_json, attachment=False
            )

    @api.constrains("wa_interactive_ids")
    def _check_wa_interactive_ids(self):
        if len(self.wa_interactive_ids) > 1:
            raise UserError(
                _(
                    "Adding more than one interactive type in a template is not supported. Please revise the template accordingly."
                )
            )
        else:
            pass

    def send_pre_message_by_whatsapp(self):
        partner_id = self.env.context.get('partner', False)
        if partner_id:
            wizard_rec = self.env['whatsapp.composer'].with_context(active_model=self.model_id.model,
                                                                    active_id=partner_id).create(
                {'partner_id': partner_id, 'wa_account_id': self.wa_account_id.id,
                 'wa_template_id': self.id})

            return wizard_rec.action_send_whatsapp_template()
