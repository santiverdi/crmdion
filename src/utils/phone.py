"""Normalizar teléfonos argentinos a formato internacional para wa.me."""

import re


def extraer_movil(telefono_raw: str) -> str:
    """Extrae el número móvil del formato TodoAlojamiento.

    Formatos posibles:
      - "Mov: +54 9 11 3702-9115 - Fij: +54 9 11 3702-9115"
      - "Mov: +54 9 11 6263-1970"
      - "Mov: 3413360302"
      - "Mov: 5492216775355"
      - "Mov: 1140852853 - Fij: 1140852853"
    """
    if not telefono_raw or not isinstance(telefono_raw, str):
        return ""

    # Tomar solo la parte móvil (antes de " - Fij:")
    parte_movil = telefono_raw.split(" - Fij:")[0]

    # Quitar prefijo "Mov: "
    parte_movil = re.sub(r'^Mov:\s*', '', parte_movil)

    return parte_movil.strip()


def normalizar_argentino(telefono: str) -> str:
    """Normaliza un teléfono argentino a formato wa.me: 549XXXXXXXXXX (sin +).

    Reglas:
      - País: 54
      - Móvil: 9
      - Código de área + número = 10 dígitos
      - Ejemplo final: 5491112345678
    """
    if not telefono:
        return ""

    # Quitar todo excepto dígitos y +
    solo_digitos = re.sub(r'[^\d+]', '', telefono)

    # Quitar el + inicial si existe
    solo_digitos = solo_digitos.lstrip('+')

    if not solo_digitos:
        return ""

    # Si empieza con 549 y tiene 13 dígitos → ya está normalizado
    if solo_digitos.startswith('549') and len(solo_digitos) == 13:
        return solo_digitos

    # Si empieza con 54 pero sin 9 (ej: 541112345678 → 12 dígitos)
    if solo_digitos.startswith('54') and not solo_digitos.startswith('549') and len(solo_digitos) == 12:
        return '549' + solo_digitos[2:]

    # Si empieza con 54 y tiene 13 pero el 9 está en posición correcta
    if solo_digitos.startswith('54') and len(solo_digitos) == 13:
        return solo_digitos

    # Si tiene 10 dígitos → es número local (área + número)
    if len(solo_digitos) == 10:
        return '549' + solo_digitos

    # Si tiene 11 dígitos y empieza con 15 → quitar 15, agregar 549 + 11
    # Esto es formato viejo de Buenos Aires: 15-XXXX-XXXX
    if len(solo_digitos) == 11 and solo_digitos.startswith('15'):
        return '54911' + solo_digitos[2:]

    # Si tiene 11 dígitos y empieza con 9 → agregar 54
    if len(solo_digitos) == 11 and solo_digitos.startswith('9'):
        return '54' + solo_digitos

    # Fallback: intentar con lo que hay
    if len(solo_digitos) >= 10:
        return '549' + solo_digitos[-10:]

    return ""


def telefono_para_wame(telefono_raw: str) -> str:
    """Pipeline completo: raw de TodoAlojamiento → número para wa.me."""
    movil = extraer_movil(telefono_raw)
    return normalizar_argentino(movil)
