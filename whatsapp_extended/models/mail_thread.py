# -*- coding: utf-8 -*-

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # Este modulo NO sobreescribe message_post.
    #
    # Hasta la migracion a v19 habia aqui una copia completa de message_post de
    # v17 cuyo unico aporte era pasar `timestamp` a los valores del mensaje. El
    # nucleo ya hace eso solo: message_post reparte sus kwargs sobrantes y los
    # que coinciden con un campo de mail.message van a parar al create
    # (mail_thread.py:2269). `timestamp` es un campo de mail.message declarado
    # en models/mail_message.py, asi que la llamada de
    # whatsapp_account.py:220-225 funciona sin ayuda.
    #
    # La copia se quedo anclada a la firma de v17 y rompia al guardar cualquier
    # registro con seguimiento:
    #   TypeError: _message_compute_author() got an unexpected keyword
    #   argument 'raise_on_email'
    # ese parametro desaparecio en v19. Detras venian mas: user_has_groups ya no
    # existe en los modelos (ahora env.user._is_internal()), record_name paso a
    # ser calculado no almacenado, y v19 agrego incoming_email_to,
    # incoming_email_cc, outgoing_email_to y la suscripcion automatica del
    # cliente, nada de lo cual tenia la copia.
    #
    # Si algun dia hace falta tocar el mensaje, hacerlo con un super() y un
    # hook, no reponiendo la copia.

    def _get_message_create_valid_field_names(self):
        res = super(MailThread, self)._get_message_create_valid_field_names()
        res.add('timestamp')
        return res