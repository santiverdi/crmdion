"""Generar links wa.me con mensaje prellenado por huésped."""

from urllib.parse import quote


def generar_link_wame(telefono_normalizado: str, mensaje: str) -> str:
    """Genera un link wa.me con mensaje prellenado.

    Args:
        telefono_normalizado: Número en formato 549XXXXXXXXXX (sin +)
        mensaje: Texto del mensaje ya personalizado

    Returns:
        URL wa.me lista para abrir, o "" si no hay teléfono
    """
    if not telefono_normalizado:
        return ""

    mensaje_encoded = quote(mensaje, safe='')
    return f"https://wa.me/{telefono_normalizado}?text={mensaje_encoded}"


def personalizar_mensaje_post_estadia(
    nombre: str,
    link_reviews: str = "https://g.page/r/HOTEL_DION_REVIEW",
    link_web: str = "https://hoteldion.com",
    fecha_vencimiento: str = "",
) -> str:
    """Personaliza el mensaje WhatsApp post-estadía para un huésped.

    Args:
        nombre: Nombre del huésped (se usa solo el primer nombre)
        link_reviews: Link de Google Reviews del hotel
        link_web: URL de reserva directa
        fecha_vencimiento: Fecha de vencimiento del cupón (formato dd/mm/yyyy)
    """
    # Extraer primer nombre y capitalizar
    primer_nombre = nombre.strip().split(",")[0].strip().split()[0].title()

    return (
        f"Hola {primer_nombre}! \U0001f44b\n"
        f"\n"
        f"Gracias por elegirnos en Hotel Dion.\n"
        f"Esperamos que hayas disfrutado tu estadia en Mar del Plata!\n"
        f"\n"
        f"Nos ayudaria mucho si nos dejas tu opinion en Google:\n"
        f"{link_reviews}\n"
        f"\n"
        f"Como agradecimiento, te regalamos un 10% OFF para tu proxima reserva directa.\n"
        f"Tu codigo: VUELVO10\n"
        f"Valido hasta {fecha_vencimiento}\n"
        f"\n"
        f"Reserva directo aca: {link_web}\n"
        f"O respondenos por aca mismo \U0001f60a\n"
        f"\n"
        f"Hotel Dion - Mar del Plata"
    )
