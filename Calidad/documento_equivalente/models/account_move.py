from odoo import models, fields
from datetime import datetime
import pytz

class AccountMove(models.Model):
    _inherit = 'account.move'

    doc_period = fields.Many2one('dian.formgentrans', string='Forma de generación y transmisión')
    documento_equivalente = fields.Boolean(string='Documento equivalente', related='journal_id.documento_equivalente')
    note_document_equivalent_concept = fields.Many2one("dian.note.document.equivalent.concept", string='Concepto Nota de ajuste')

    def get_nombreplantilla(self, move):
        tipo = move.GetInvoiceType(move)
        if tipo in ['05', '95']:
            return 'plantillaDS.xml'
        else:
            return super(AccountMove, self).get_nombreplantilla(move)

    def GetInvoiceType(self):
        res = super(AccountMove, self).GetInvoiceType()
        for dato in self:
            if res == '':
                if dato.move_type == 'in_invoice' and dato.documento_equivalente:
                    return '05'
                elif dato.move_type == 'in_refund' and dato.documento_equivalente:
                    return '95'
            return res

    def get_url_ws(self, invoicetype):
        ip_ws = str(self.company_id.ip_webservice)
        url = ''
        if invoicetype == '05':
            return 'http://' + ip_ws + '/api/EnvioDocumentoEquivalente'
        elif invoicetype == '95':
            return 'http://' + ip_ws + '/api/EnvioNotaDocumentoEquivalente'
        else:
            return super(AccountMove, self).get_url_ws(invoicetype)

    def create_dict_invoicehead_dian(self, totales):
        invoicetype = self.GetInvoiceType()
        datos = super(AccountMove, self).create_dict_invoicehead_dian(totales)

        if invoicetype == "05":
            datos['InvoiceComment1'] = ''

            # Lista de campos que se deben eliminar cuando invoicetype es "05"
            fields_to_remove = [
                'InvoiceTypeRef', 'InvoiceDateRef', 'DueDateRef',
                'InvoicePeriod', 'NetWeight', 'PorcAdministracion',
                'PorcImprevistos', 'PorcUtilidad', 'GrossWeight'
            ]

            # Eliminar todos los campos en la lista
            for field in fields_to_remove:
                datos.pop(field, None)  # Usar pop con None para evitar errores si el campo no existe

        return datos

    def obtener_resolucion_encabezado(self, invoice_type):
        if invoice_type == '95':
            reversed_entry = self.reversed_entry_id
            journal_resolution = self.journal_id.refund_sequence_id.resolution_id
            inv_date = self.invoice_date
            rate = 1 / self.currency_id.with_context(date=inv_date).rate

            return {
                'InvoiceRef': reversed_entry.name,
                'InvoiceRefCufe': reversed_entry.cufe if reversed_entry else "",
                'InvoiceTypeRef': reversed_entry.GetInvoiceType(),
                'InvoiceDateRef': reversed_entry.invoice_date.strftime('%d/%m/%Y %H:%M:%S'),
                'DueDateRef': reversed_entry.invoice_date_due.strftime('%d/%m/%Y %H:%M:%S'),
                'DiscrepansyDescription': self.note_document_equivalent_concept.name,
                'DiscrepansyCode': self.note_document_equivalent_concept.code,
                'CMReasonCode_c': '0',
                'CMReasonDesc_c': '0',
                'DMReasonCode_c': '0',
                'DMReasonDesc_c': '0',
                'CalculationRate_c': f"{rate:.2f}",
                'DateCalculationRate_c': inv_date.strftime('%Y-%m-%d'),
                'Resolution': journal_resolution.resolution_resolution,
                'ResolutionPrefix': self.journal_id.refund_sequence_id.prefix,
                'ResolutionDateInvoice': journal_resolution.resolution_resolution_date.strftime('%Y-%m-%d'),
                'ResolutionDateFrom': journal_resolution.resolution_date_from.strftime('%Y-%m-%d'),
                'ResolutionDateTo': journal_resolution.resolution_date_to.strftime('%Y-%m-%d'),
                'ResolutionRankFrom': str(journal_resolution.resolution_from),
                'ResolutionRankTo': str(journal_resolution.resolution_to),
                'TecnicalKey': ' '
            }
        else:
            return super(AccountMove, self).obtener_resolucion_encabezado(invoice_type)

    def create_dict_customer(self):
        invoicetype = self.GetInvoiceType()

        if invoicetype not in ['05', '95']:
            return super(AccountMove, self).create_dict_customer()

        company = self.company_id
        nit_company = self.GetNitCompany(company.vat)
        fiscal_responsibility = self.GetResponsibilities(company.fiscal_responsibility_ids)

        return {
            'Company': nit_company,
            'CustID': company.document_type_id.code,
            'CustNum': nit_company,
            'ResaleID': nit_company,
            'Name': company.name,
            'Address1': company.street,
            'EMailAddress': company.email,
            'PhoneNum': company.phone,
            'CurrencyCode': self.currency_id.name,
            'Country': company.country_id.name,
            'CountryCode': company.country_id.code,
            'PostalZone': company.zip,
            'RegimeType_c': company.company_type_id.code,
            'FiscalResposability_c': fiscal_responsibility,
            'State': company.state_id.name,
            'StateNum': company.state_id.dian_state_code,
            'City': company.city_id.name,
            'CityNum': company.city_id.code,
            'CorporateRegistration': company.commercial_registration
        }

    def create_dict_company_dian(self):
        invoicetype = self.GetInvoiceType()

        if invoicetype not in ['05', '95']:
            return super(AccountMove, self).create_dict_company_dian()

        partner = self.partner_id
        cust_num = self.GetNitCompany(partner.vat)
        cust_id = self.TypeDocumentCust(partner.l10n_latam_identification_type_id.l10n_co_document_code)
        fiscal_responsibility_partner = self.GetResponsibilities(partner.fiscal_responsibility_partner_ids)

        # Obtener la zona horaria del usuario o UTC por defecto
        local_tz = pytz.timezone(self.env.user.tz or 'UTC')

        # Obtener la fecha y hora actual en la zona horaria correspondiente
        now = datetime.now(local_tz)
        order_num, date_order = " ", now.strftime('%d/%m/%Y %H:%M:%S')

        if self.invoice_origin:
            invoice_origin = self.env['purchase.order'].search([('name', '=', self.invoice_origin)], limit=1)
            if invoice_origin:
                order_num = invoice_origin.name
                date_order = invoice_origin.date_approve.strftime('%d/%m/%Y %H:%M:%S')
            else:
                order_num = self.invoice_origin

        return {
            'company': cust_num,
            'StateTaxID': cust_num,
            'IdentificationType': cust_id,
            'Name': partner.name,
            'RegimeType_c': partner.organization_type_id.code,
            'FiscalResposability_c': fiscal_responsibility_partner,
            'CompanyType_c': partner.organization_type_id.code,
            'State': partner.state_id.name,
            'StateNum': partner.state_id.dian_state_code,
            'City': partner.city_id.name,
            'CityNum': partner.city_id.code,
            'Address1': partner.street,
            'CurrencyCode': self.currency_id.name,
            'CountryName': partner.country_id.name,
            'CountryCode': partner.country_id.code,
            'OrderNum': order_num,
            'DateOrder': date_order,
            'PostalZone': partner.zip,
            'PhoneNum': partner.phone,
            'Email': partner.email,
            'WebPage': partner.website,
            'CorporateRegistration': partner.commercial_registration_partner,
            'TypeOfOrigin': partner.type_of_origin_id.code
        }