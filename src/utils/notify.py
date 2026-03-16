"""Enviar notificación al conserje cuando llega un nuevo lead."""

import json
import os
import urllib.request
import urllib.error


def notificar_conserje(lead: dict) -> bool:
    """Envía notificación del nuevo lead al conserje vía webhook.

    El webhook puede ser de Make.com, n8n, o Zapier.
    Estos servicios luego envían la notificación por:
    - Telegram (recomendado, gratis e instantáneo)
    - Email
    - Push notification

    Args:
        lead: Diccionario con datos del lead

    Returns:
        True si la notificación se envió correctamente
    """
    webhook_url = os.environ.get('WEBHOOK_NOTIFY_URL', '')

    if not webhook_url:
        print(f"[NOTIFY] Sin webhook configurado. Lead #{lead.get('id', '?')}: {lead['nombre']}")
        return False

    # Formatear mensaje legible
    noches = _calcular_noches(lead.get('checkin', ''), lead.get('checkout', ''))
    personas = f"{lead.get('adultos', 1)} adultos"
    if lead.get('menores', 0) > 0:
        personas += f" + {lead['menores']} menores"

    mensaje = (
        f"NUEVO LEAD - Hotel Dion\n"
        f"{'=' * 30}\n"
        f"Nombre: {lead['nombre']}\n"
        f"Teléfono: {lead['telefono']}\n"
        f"Email: {lead.get('email', '-')}\n"
        f"Check-in: {lead['checkin']}\n"
        f"Check-out: {lead['checkout']} ({noches} noches)\n"
        f"Personas: {personas}\n"
        f"Habitación: {lead['tipo_habitacion']}\n"
    )

    if lead.get('mensaje'):
        mensaje += f"Mensaje: {lead['mensaje']}\n"

    payload = {
        'text': mensaje,
        'lead': lead,
    }

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status < 400
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"[NOTIFY] Error enviando webhook: {e}")
        return False


def _calcular_noches(checkin: str, checkout: str) -> int:
    """Calcula noches entre dos fechas."""
    try:
        from datetime import datetime
        ci = datetime.strptime(checkin, '%Y-%m-%d')
        co = datetime.strptime(checkout, '%Y-%m-%d')
        return (co - ci).days
    except (ValueError, TypeError):
        return 0
