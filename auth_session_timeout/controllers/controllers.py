from odoo import http
from odoo.http import request, SessionExpiredException
from odoo.addons.website_sale.controllers.main import WebsiteSale  # Importa el controlador original
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect


class WebsiteSaleSessionCheck(WebsiteSale):

    # Sobrescribe la ruta que maneja la creación/actualización de la transacción de pago
    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:order_id>'],
                type='json', auth="public", website=True)
    def payment_transaction(self, *args, **kwargs):

        # --- Lógica de Verificación de Sesión ---
        # 1. Chequeo Rápido: Si no hay UID, o si ya se detectó que expiró (aunque es más seguro verificar la sesión)
        if not request.session.uid or request.env.user._auth_timeout_check():
            pass  # Si la lógica de _auth_timeout_check lanza la excepción, no necesitas hacer más.

        # Si el código llega aquí, la sesión es válida o la excepción ya se lanzó y el flujo se interrumpió.
        order = request.website.sale_get_order()
        if not order:
            # Manejar el error si no hay orden, aunque esto no debería ocurrir aquí
            raise http.request.not_found()

        if 'partner_id' not in kwargs:
            kwargs['partner_id'] = order.partner_id.id

        if 'currency_id' not in kwargs:
            kwargs['currency_id'] = order.currency_id.id

        return super(WebsiteSaleSessionCheck, self).payment_transaction(*args, **kwargs)
