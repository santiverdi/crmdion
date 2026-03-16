"""Script post-estadía automático para Hotel Dion.

Lee el export de TodoAlojamiento, detecta checkouts de ayer, y genera:
1. HTML con links wa.me para que el conserje mande con un tap
2. Programa email día +3 vía Brevo API
3. Loguea en CSV quién fue contactado

Uso:
    python src/post_estadia.py --excel path/al/export.xlsx
    python src/post_estadia.py --excel path/al/export.xlsx --fecha 2026-03-14
    python src/post_estadia.py --excel path/al/export.xlsx --solo-html
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Agregar src/ al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.phone import telefono_para_wame
from utils.whatsapp import generar_link_wame, personalizar_mensaje_post_estadia

# --- Configuración ---
HOTEL_ROW_START = 6759  # Fila header de Hotel Dion en el Excel multi-hotel
LINK_REVIEWS = "https://g.page/r/HOTEL_DION_REVIEW"  # TODO: reemplazar con link real
LINK_WEB = "https://hoteldion.com"  # TODO: reemplazar con link real
OUTPUT_DIR = Path(__file__).parent.parent / "Hotel-Brain" / "07 - Campañas" / "Hotel-Dion"
LOG_CSV = OUTPUT_DIR / "log_post_estadia.csv"


def cargar_excel(path: str, fecha_referencia: datetime) -> pd.DataFrame:
    """Carga el Excel de TodoAlojamiento y filtra checkouts de ayer."""
    df_raw = pd.read_excel(path, header=None)

    # Detectar si es multi-hotel o single-hotel
    # Si tiene más de 7000 filas, probablemente es multi-hotel
    if len(df_raw) > 7000:
        header_row = HOTEL_ROW_START
    else:
        # Single hotel: buscar la fila header
        for i, row in df_raw.iterrows():
            if str(row.iloc[0]).strip() == 'Nro':
                header_row = i
                break
        else:
            header_row = 0

    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = df_raw.iloc[header_row].values
    df = df[df.iloc[:, 0] != 'TOTALES:'].dropna(subset=[df.columns[0]])
    df = df[~df.iloc[:, 0].astype(str).str.startswith('Hotel')]
    df = df[df.iloc[:, 0] != 'Nro']

    # Filtrar canceladas
    estados_excluir = [
        'Cancelada por el pasajero',
        'Cancelada por falta de respuesta',
        'No Show',
        'Pago Rechazado',
    ]
    df = df[~df['Estado'].isin(estados_excluir)]

    # Parsear fechas
    df['Salida_dt'] = pd.to_datetime(df['Salida'], errors='coerce', dayfirst=True)

    # Checkouts de ayer
    ayer = fecha_referencia - timedelta(days=1)
    checkouts = df[df['Salida_dt'].dt.date == ayer.date()].copy()

    return checkouts


def generar_html(contactos: list[dict], fecha: str) -> str:
    """Genera HTML con links wa.me para el conserje."""
    rows = ""
    for c in contactos:
        link = c.get('link_wame', '')
        nombre = c['nombre']
        telefono = c.get('telefono_normalizado', '')
        email = c.get('email', '')

        if link:
            boton = f'<a href="{link}" target="_blank" class="btn">Enviar WhatsApp</a>'
        else:
            boton = '<span class="no-tel">Sin teléfono válido</span>'

        rows += f"""
        <tr>
            <td><strong>{nombre}</strong></td>
            <td>{telefono}</td>
            <td>{email}</td>
            <td>{boton}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post-Estadía - Checkouts {fecha}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #f5f5f5; }}
        h1 {{ margin-bottom: 10px; color: #1a1a1a; }}
        .info {{ color: #666; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #2c3e50; color: white; padding: 12px 16px; text-align: left; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .btn {{ background: #25D366; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 600; display: inline-block; }}
        .btn:hover {{ background: #1da851; }}
        .no-tel {{ color: #e74c3c; font-size: 0.85em; }}
        .count {{ background: #25D366; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9em; margin-left: 10px; }}
    </style>
</head>
<body>
    <h1>Post-Estadía Hotel Dion <span class="count">{len(contactos)} huéspedes</span></h1>
    <p class="info">Checkouts del {fecha} — Toca el botón para enviar el WhatsApp</p>
    <table>
        <thead>
            <tr>
                <th>Huésped</th>
                <th>Teléfono</th>
                <th>Email</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table>
</body>
</html>"""


def programar_email_brevo(contactos: list[dict], fecha_envio: datetime):
    """Programa emails día +3 vía Brevo API.

    Requiere BREVO_API_KEY en variables de entorno.
    Si no está configurada, solo loguea lo que haría.
    """
    api_key = os.environ.get('BREVO_API_KEY', '')

    if not api_key:
        print("\n[BREVO] No hay BREVO_API_KEY configurada.")
        print(f"[BREVO] Se programarían {len(contactos)} emails para {fecha_envio.strftime('%d/%m/%Y')}")
        print("[BREVO] Configurá la variable de entorno para activar el envío automático.")
        return

    try:
        import sib_api_v3_sdk
    except ImportError:
        print("\n[BREVO] Instalá el SDK: pip install sib-api-v3-sdk")
        print(f"[BREVO] Se programarían {len(contactos)} emails para {fecha_envio.strftime('%d/%m/%Y')}")
        return

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    enviados = 0
    for c in contactos:
        email = c.get('email', '')
        if not email or '@' not in email or 'nomail' in email.lower() or 'notiene' in email.lower():
            continue

        nombre = c['nombre'].strip().split(",")[0].strip().split()[0].title()

        send_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email, "name": c['nombre']}],
            sender={"name": "Hotel Dion", "email": "reservas@hoteldion.com"},
            subject=f"{nombre}, tu opinión nos importa + regalo inside",
            html_content=_generar_email_html(nombre),
            scheduled_at=fecha_envio.isoformat(),
        )

        try:
            api_instance.send_transac_email(send_email)
            enviados += 1
        except Exception as e:
            print(f"[BREVO] Error enviando a {email}: {e}")

    print(f"\n[BREVO] {enviados} emails programados para {fecha_envio.strftime('%d/%m/%Y')}")


def _generar_email_html(nombre: str) -> str:
    """Genera el HTML del email post-estadía."""
    return f"""
    <div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Hola {nombre},</h2>
        <p>Fue un placer tenerte en <strong>Hotel Dion</strong>.</p>
        <p>Queremos seguir mejorando y tu opinión es clave.<br>¿Nos regalás 2 minutos?</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{LINK_REVIEWS}" style="background: #4285f4; color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px;">
                Dejar mi opinión en Google
            </a>
        </p>
        <p>Como agradecimiento:</p>
        <ul>
            <li><strong>10% OFF</strong> en tu próxima reserva directa</li>
            <li>Código: <strong>VUELVO10</strong></li>
        </ul>
        <p>Reservá directo en <a href="{LINK_WEB}">{LINK_WEB}</a> o escribinos al WhatsApp.<br>
        Siempre es mejor que Booking 😉</p>
        <p style="margin-top: 30px; color: #666;">¡Hasta la próxima!<br><strong>Equipo Hotel Dion</strong></p>
    </div>
    """


def loguear_contactados(contactos: list[dict], fecha: str):
    """Registra en CSV quién fue contactado."""
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)

    archivo_nuevo = not LOG_CSV.exists()

    with open(LOG_CSV, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'fecha_checkout', 'fecha_contacto', 'nombre', 'telefono',
            'email', 'wa_enviado', 'email_programado',
        ])
        if archivo_nuevo:
            writer.writeheader()

        for c in contactos:
            tiene_wa = bool(c.get('link_wame'))
            tiene_email = bool(c.get('email')) and '@' in str(c.get('email', ''))
            writer.writerow({
                'fecha_checkout': fecha,
                'fecha_contacto': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'nombre': c['nombre'],
                'telefono': c.get('telefono_normalizado', ''),
                'email': c.get('email', ''),
                'wa_enviado': 'pendiente' if tiene_wa else 'sin_telefono',
                'email_programado': 'programado' if tiene_email else 'sin_email',
            })

    print(f"[LOG] Registrados {len(contactos)} contactos en {LOG_CSV}")


def main():
    parser = argparse.ArgumentParser(description='Post-estadía automático Hotel Dion')
    parser.add_argument('--excel', required=True, help='Path al Excel de TodoAlojamiento')
    parser.add_argument('--fecha', help='Fecha de referencia (YYYY-MM-DD). Default: hoy')
    parser.add_argument('--solo-html', action='store_true', help='Solo generar HTML, no enviar emails')
    args = parser.parse_args()

    fecha_ref = datetime.strptime(args.fecha, '%Y-%m-%d') if args.fecha else datetime.now()
    ayer = fecha_ref - timedelta(days=1)
    fecha_str = ayer.strftime('%Y-%m-%d')
    fecha_vencimiento = (ayer + timedelta(days=90)).strftime('%d/%m/%Y')

    print(f"=== Post-Estadía Hotel Dion ===")
    print(f"Buscando checkouts del {fecha_str}...")

    checkouts = cargar_excel(args.excel, fecha_ref)

    if checkouts.empty:
        print(f"No hay checkouts del {fecha_str}.")
        return

    print(f"Encontrados: {len(checkouts)} checkouts")

    # Agrupar por pasajero (puede haber múltiples habitaciones)
    contactos = []
    for nombre, grupo in checkouts.groupby('Pasajero'):
        fila = grupo.iloc[0]
        tel_raw = str(fila.get('Telefono', ''))
        tel_norm = telefono_para_wame(tel_raw)
        email = str(fila.get('Mail', ''))

        mensaje = personalizar_mensaje_post_estadia(
            nombre=str(nombre),
            link_reviews=LINK_REVIEWS,
            link_web=LINK_WEB,
            fecha_vencimiento=fecha_vencimiento,
        )

        link = generar_link_wame(tel_norm, mensaje)

        contactos.append({
            'nombre': str(nombre),
            'telefono_raw': tel_raw,
            'telefono_normalizado': tel_norm,
            'email': email,
            'link_wame': link,
            'mensaje': mensaje,
        })

    print(f"Huéspedes únicos: {len(contactos)}")
    con_wa = sum(1 for c in contactos if c['link_wame'])
    print(f"Con WhatsApp válido: {con_wa}")

    # 1. Generar HTML
    html = generar_html(contactos, fecha_str)
    html_path = OUTPUT_DIR / f"post_estadia_{fecha_str}.html"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding='utf-8')
    print(f"\n[HTML] Generado: {html_path}")

    # 2. Programar emails día +3
    if not args.solo_html:
        fecha_email = ayer + timedelta(days=3)
        programar_email_brevo(contactos, fecha_email)

    # 3. Loguear
    loguear_contactados(contactos, fecha_str)

    print(f"\n--- Listo. Abrí {html_path.name} y tocá los botones de WhatsApp. ---")


if __name__ == '__main__':
    main()
