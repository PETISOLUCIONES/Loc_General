# -*- coding: utf-8 -*-

import logging
import threading
import time
import re
from odoo.http import request
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class WhatsappAccountInherit(models.Model):
    _inherit = "whatsapp.account"

    def simulate_whatsapp_message_reception(self, sender_mobile="+57 305-220-0862", message_body="Hola"):
        def format_phone_number(phone_number):
            phone_number = re.sub(r"\s+", "", phone_number)
            phone_number = re.sub(r"\-", "", phone_number)
            phone_number = re.sub(r"\+", "", phone_number)
            phone_number = re.sub(r"\(", "", phone_number)
            phone_number = re.sub(r"\)", "", phone_number)
            return phone_number

        '''
        Ejemplo de valor simulado:

        value: {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": "15556256247",
                "phone_number_id": "390366274159579"
            },
            "statuses": [
                {
                    "id": "wamid.HBgMNTczMDUyMjAwODYyFQIAERgSRDQxRjJEOTg4MUZENDlFOEJFAA==",
                    "status": "sent",
                    "timestamp": "1729198401",
                    "recipient_id": "573052200862",
                    "conversation": {
                        "id": "a54f04001ffd9c864563254a6dc468e7",
                        "expiration_timestamp": "1729270200",
                        "origin": {
                            "type": "service"
                        }
                    },
                    "pricing": {
                        "billable": true,
                        "pricing_model": "CBP",
                        "category": "service"
                    }
                }
            ]
        }
        '''

        # Quitar espacios, guiones, parentesis y signo de suma de los números de teléfono
        display_phone_number = format_phone_number(self.display_phone_number)
        sender_mobile = format_phone_number(sender_mobile)

        # Simula el valor recibido desde el webhook de WhatsApp
        simulated_value = {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": display_phone_number,  # Obtiene el número de teléfono de la cuenta de WhatsApp FORMATEADO
                "phone_number_id": self.phone_uid,  # Obtiene el ID del número de teléfono de la cuenta de WhatsApp
            },
            "contacts": [
                {
                    "profile": {
                        "name": "Test Johan"  # Nombre ficticio del remitente
                    },
                    "wa_id": sender_mobile,  # Número de teléfono del remitente FORMATEADO
                }
            ],
            "messages": [
                {
                    "from": sender_mobile, # Número de teléfono del remitente FORMATEADO
                    "id": "wamid.fake-message-id-" + str(time.time()),  # Genera un ID ficticio usando el timestamp actual
                    "timestamp": str(int(time.time())),  # Timestamp actual
                    "text": {
                        "body": message_body  # Cuerpo del mensaje
                    },
                    "type": "text"  # Tipo de mensaje (en este caso, texto)
                }
            ]
        }

        # Llamar al método que procesa los mensajes, como lo haría el webhook real
        request.env['whatsapp.message']._process_statuses(simulated_value)
        self._process_messages(simulated_value)

    def simulate_whatsapp_location_reception(self, sender_mobile="+57 305-220-0862", latitude=4.8014858, longitude=-75.6916669):
        def format_phone_number(phone_number):
            phone_number = re.sub(r"\s+", "", phone_number)
            phone_number = re.sub(r"\-", "", phone_number)
            phone_number = re.sub(r"\+", "", phone_number)
            phone_number = re.sub(r"\(", "", phone_number)
            phone_number = re.sub(r"\)", "", phone_number)
            return phone_number

        '''
        Ejemplo de valor simulado:

        value: {
            'messaging_product': 'whatsapp',
            'metadata': {
                'display_phone_number': '573113735042',
                'phone_number_id': '386741851186729'
            },
            'contacts': [{
                'profile': {
                    'name': 'Johan Acuña'
                },
                'wa_id': '573106355956'
            }],
            'messages': [{
                'from': '573106355956',
                'id': 'wamid.HBgMNTczMTA2MzU1OTU2FQIAEhggMDE0Rjc2RTc3NDI1RTVBRjhDQzkxMkQzNzZERDY3NUEA',
                'timestamp': '1738849940',
                'location': {
                    'latitude': 4.8014858,
                    'longitude': -75.6916669
                },
                'type': 'location'
            }]
        }
        '''

        # Quitar espacios, guiones, parentesis y signo de suma de los números de teléfono
        display_phone_number = format_phone_number(self.display_phone_number)
        sender_mobile = format_phone_number(sender_mobile)

        # Simula el valor recibido desde el webhook de WhatsApp
        simulated_value = {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": display_phone_number,  # Obtiene el número de teléfono de la cuenta de WhatsApp FORMATEADO
                "phone_number_id": self.phone_uid,  # Obtiene el ID del número de teléfono de la cuenta de WhatsApp
            },
            "contacts": [
                {
                    "profile": {
                        "name": "Test Johan"  # Nombre ficticio del remitente
                    },
                    "wa_id": sender_mobile,  # Número de teléfono del remitente FORMATEADO
                }
            ],
            "messages": [
                {
                    "from": sender_mobile, # Número de teléfono del remitente FORMATEADO
                    "id": "wamid.fake-message-id-" + str(time.time()),  # Genera un ID ficticio usando el timestamp actual
                    "timestamp": str(int(time.time())),  # Timestamp actual
                    "location": {
                        'latitude': latitude,  # Latitud de la ubicación
                        'longitude': longitude  # Longitud de la ubicación
                    },
                    "type": "location"  # Tipo de mensaje (en este caso, ubicación)
                }
            ]
        }

        # Llamar al método que procesa los mensajes, como lo haría el webhook real
        request.env['whatsapp.message']._process_statuses(simulated_value)
        self._process_messages(simulated_value)

    def simulate_whatsapp_image_reception(self, sender_mobile="+57 305-220-0862", images="1"):
        def format_phone_number(phone_number):
            phone_number = re.sub(r"\s+", "", phone_number)
            phone_number = re.sub(r"\-", "", phone_number)
            phone_number = re.sub(r"\+", "", phone_number)
            phone_number = re.sub(r"\(", "", phone_number)
            phone_number = re.sub(r"\)", "", phone_number)
            return phone_number

        '''
        Ejemplo de valor simulado:
        value: {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": "15556256247",
                "phone_number_id": "390366274159579"
            },
            "contacts": [
                {
                    "profile": {
                        "name": "PETI Test (Johan)"
                    },
                    "wa_id": "573052200862"
                }
            ],
            "messages": [
                {
                    "from": "573052200862",
                    "id": "wamid.HBgMNTczMDUyMjAwODYyFQIAEhggMzc5MDYyRTY5Q0JGOUJEOTE2NzEzNDVGRDk2MTc2OTEA",
                    "timestamp": "1729198397",
                    "type": "image",
                    "image": {
                        "mime_type": "image/jpeg",
                        "sha256": "mTUViLq1rc6RyoR0n0g04znCZdqWB2xv63UI5Fw0iCQ=",
                        "id": "1264851604538831"
                    }
                }
            ]
        '''

        # Quitar espacios, guiones, parentesis y signo de suma de los números de teléfono
        display_phone_number = format_phone_number(self.display_phone_number)
        sender_mobile = format_phone_number(sender_mobile)

        # Función para simular el mensaje de "Terminar"
        def send_finish_message():
            self.simulate_whatsapp_message_reception(sender_mobile, "Terminar")

        for i in range(int(images)):
            # Test para interrumpir el envío de imágenes
            if (int(images) == 5 and i == 2) or (int(images) == 10 and i == 5):
                finish_thread = threading.Thread(target=send_finish_message)
                finish_thread.start()
                finish_thread.join()

            # Simula el valor recibido desde el webhook de WhatsApp para un mensaje de imagen
            simulated_value = {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": display_phone_number,
                    # Número de teléfono de la cuenta de WhatsApp FORMATEADO
                    "phone_number_id": self.phone_uid,  # ID del número de teléfono de la cuenta de WhatsApp
                },
                "contacts": [
                    {
                        "profile": {
                            "name": "Test Johan"  # Nombre ficticio del remitente
                        },
                        "wa_id": sender_mobile,  # Número de teléfono del remitente FORMATEADO
                    }
                ],
                "messages": [
                    {
                        "from": sender_mobile,  # Número de teléfono del remitente FORMATEADO
                        "id": "HBgMNTczMDUyMjAwODYyFQIAEhggMzc5MDYyRTY5Q0JGOUJEOTE2NzEzNDVGRDk2MTc2OTEA",
                        # Genera un ID ficticio usando el timestamp actual
                        "timestamp": str(int(time.time())),  # Timestamp actual
                        "type": "image",  # Tipo de mensaje (en este caso, imagen)
                        "image": {
                            "mime_type": "image/jpeg",  # Tipo MIME de la imagen
                            "sha256": "mTUViLq1rc6RyoR0n0g04znCZdqWB2xv63UI5Fw0iCQ",
                            "id": "1264851604538831"  # ID ficticio de la imagen
                        }
                    }
                ]
            }

            # Llamar al método que procesa los mensajes, como lo haría el webhook real
            request.env['whatsapp.message']._process_statuses(simulated_value)
            self._process_messages(simulated_value)

    def simulate_whatsapp_image_reception2(self, sender_mobile="+57 305-220-0862", images="1"):
        def format_phone_number(phone_number):
            phone_number = re.sub(r"\s+", "", phone_number)
            phone_number = re.sub(r"\-", "", phone_number)
            phone_number = re.sub(r"\+", "", phone_number)
            phone_number = re.sub(r"\(", "", phone_number)
            phone_number = re.sub(r"\)", "", phone_number)
            return phone_number

        '''
        Ejemplo de valor simulado:
        value: {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": "15556256247",
                "phone_number_id": "390366274159579"
            },
            "contacts": [
                {
                    "profile": {
                        "name": "PETI Test (Johan)"
                    },
                    "wa_id": "573052200862"
                }
            ],
            "messages": [
                {
                    "from": "573052200862",
                    "id": "wamid.HBgMNTczMDUyMjAwODYyFQIAEhggMzc5MDYyRTY5Q0JGOUJEOTE2NzEzNDVGRDk2MTc2OTEA",
                    "timestamp": "1729198397",
                    "type": "image",
                    "image": {
                        "mime_type": "image/jpeg",
                        "sha256": "mTUViLq1rc6RyoR0n0g04znCZdqWB2xv63UI5Fw0iCQ=",
                        "id": "1264851604538831"
                    }
                }
            ]
        '''

        # Quitar espacios, guiones, parentesis y signo de suma de los números de teléfono
        display_phone_number = format_phone_number(self.display_phone_number)
        sender_mobile = format_phone_number(sender_mobile)

        # Función para simular la recepción de imágenes
        def send_image(i):
            simulated_value = {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": display_phone_number,
                    "phone_number_id": self.phone_uid,  # ID del número de teléfono de la cuenta de WhatsApp
                },
                "contacts": [
                    {
                        "profile": {"name": "Test Johan"},  # Nombre ficticio del remitente
                        "wa_id": sender_mobile,  # Número de teléfono del remitente FORMATEADO
                    }
                ],
                "messages": [
                    {
                        "from": sender_mobile,  # Número de teléfono del remitente FORMATEADO
                        "id": f"wamid.fake-image-id-{i}-{str(int(time.time()))}",  # Genera un ID ficticio
                        "timestamp": str(int(time.time())),  # Timestamp actual
                        "type": "image",  # Tipo de mensaje (imagen)
                        "image": {
                            "mime_type": "image/jpeg",  # Tipo MIME de la imagen
                            "sha256": "mTUViLq1rc6RyoR0n0g04znCZdqWB2xv63UI5Fw0iCQ",  # Hash ficticio
                            "id": "1264851604538831"  # ID ficticio de la imagen
                        }
                    }
                ]
            }

            # Llamar al método que procesa los mensajes
            request.env['whatsapp.message']._process_statuses(simulated_value)
            self._process_messages(simulated_value)

        # Función para simular el mensaje de "Terminar"
        def send_finish_message():
            self.simulate_whatsapp_message_reception(sender_mobile, "Terminar")

        # Crear y empezar hilos para enviar imágenes
        image_threads = []
        for i in range(int(images)):
            image_thread = threading.Thread(target=send_image, args=(i,))
            image_threads.append(image_thread)
            image_thread.start()

            # Simular que el usuario envía el mensaje "Terminar" después de ciertas imágenes
            if (int(images) == 5 and i == 2) or (int(images) == 10 and i == 5):
                finish_thread = threading.Thread(target=send_finish_message)
                finish_thread.start()
                finish_thread.join()  # Esperar a que el mensaje "Terminar" sea enviado

        # Esperar a que todos los hilos de imágenes terminen
        for image_thread in image_threads:
            image_thread.join()
