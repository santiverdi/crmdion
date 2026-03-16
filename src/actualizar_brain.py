"""Actualizar el Hotel Brain completo con un nuevo export de TodoAlojamiento.

Un solo comando que:
1. Importa los 6 hoteles (perfiles .md en 01 - Huespedes/)
2. Genera CSVs de campaña por hotel (07 - Campañas/)
3. Genera CSVs de segmentación para Hotel Dion (particulares)
4. Genera lotes de WhatsApp para Dion
5. Actualiza analytics
6. Todo con fecha de HOY

Uso:
    python src/actualizar_brain.py --excel "C:\\ruta\\al\\export.xlsx"
    python src/actualizar_brain.py --excel "C:\\ruta\\al\\export.xlsx" --solo-dion
    python src/actualizar_brain.py --excel "C:\\ruta\\al\\export.xlsx" --fecha 2026-03-16
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# --- Paths ---
VAULT = Path(__file__).parent.parent / "Hotel-Brain"
HUESPEDES = VAULT / "01 - Huespedes"
CAMPANAS = VAULT / "07 - Campañas"
ANALYTICS = VAULT / "06 - Analytics"

# Hoteles y sus filas de inicio en el Excel multi-hotel
SEPARATORS = {
    2: 'Hotel Prince',
    1063: 'Hotel Kings',
    2852: 'Hotel VIPS',
    4298: 'Hotel America',
    4928: 'Hotel Valles',
    6757: 'Hotel Dion',
}

ESTADOS_EXCLUIR = [
    'Cancelada por el pasajero',
    'Cancelada por falta de respuesta',
    'No Show',
    'Pago Rechazado',
]


def limpiar(nombre):
    if pd.isna(nombre):
        return "Sin nombre"
    return re.sub(r'[<>:"/\\|?*]', '', str(nombre)).strip()


def segmentar(visitas, gasto, adultos, menores):
    if visitas >= 3 or gasto > 800000:
        seg, score = "VIP", 90
    elif visitas >= 2:
        seg, score = "Recurrente", 70
    else:
        seg, score = "Primera vez", 40

    if menores > 0:
        tipo = "Familia"
    elif adultos == 2:
        tipo = "Pareja"
    elif adultos == 1:
        tipo = "Solo"
    else:
        tipo = "Grupo"

    return seg, score, tipo


def parsear_excel(excel_path: str) -> dict[str, pd.DataFrame]:
    """Parsea el Excel multi-hotel y retorna dict {hotel_name: dataframe}."""
    print(f"Leyendo {excel_path}...")
    df_raw = pd.read_excel(excel_path, header=None)
    print(f"  {len(df_raw)} filas totales")

    sep_rows = sorted(SEPARATORS.keys())
    all_hotels = {}

    for idx, start_row in enumerate(sep_rows):
        hotel_name = SEPARATORS[start_row]
        header_row = start_row + 2
        end_row = sep_rows[idx + 1] if idx + 1 < len(sep_rows) else len(df_raw)

        section = df_raw.iloc[header_row + 1:end_row].copy()
        section.columns = df_raw.iloc[header_row].values
        section = section[section.iloc[:, 0] != 'TOTALES:']
        section = section.dropna(subset=[section.columns[0]])
        section = section[~section.iloc[:, 0].astype(str).str.startswith('Hotel')]
        section = section[section.iloc[:, 0] != 'Nro']
        section['Hotel'] = hotel_name

        for col in ['Total', 'Total Alojamiento', 'T. Promedio', 'Adultos',
                     'Menores', 'Infantes', 'Noc.', 'Noc. V', 'Saldo']:
            if col in section.columns:
                section[col] = pd.to_numeric(section[col], errors='coerce').fillna(0)

        all_hotels[hotel_name] = section
        print(f"  {hotel_name}: {len(section)} reservas")

    return all_hotels


def crear_perfiles(all_hotels: dict[str, pd.DataFrame]):
    """Crea/actualiza perfiles .md por huésped por hotel."""
    print("\n--- Creando perfiles de huéspedes ---")
    total = 0

    for hotel_name, df_hotel in all_hotels.items():
        safe_name = hotel_name.replace(' ', '-')
        hotel_path = HUESPEDES / safe_name
        hotel_path.mkdir(parents=True, exist_ok=True)

        df_act = df_hotel[~df_hotel['Estado'].isin(ESTADOS_EXCLUIR)]
        creados = 0

        for nombre_raw, grupo in df_act.groupby('Pasajero'):
            nombre = limpiar(nombre_raw)
            if not nombre or nombre == "Sin nombre":
                continue

            grupo = grupo.sort_values('Llegada') if 'Llegada' in grupo.columns else grupo
            visitas = len(grupo)
            gasto = grupo['Total'].sum()
            gasto_aloj = grupo['Total Alojamiento'].sum() if 'Total Alojamiento' in grupo.columns else 0
            promedio = round(gasto / visitas, 0) if visitas > 0 else 0
            adultos_max = int(grupo['Adultos'].max())
            menores_max = int(grupo['Menores'].max())
            seg, score, tipo_viajero = segmentar(visitas, gasto, adultos_max, menores_max)

            canal = grupo['Origen'].mode().iloc[0] if 'Origen' in grupo.columns and len(grupo) > 0 else ""
            mercado = grupo['Mercado'].mode().iloc[0] if 'Mercado' in grupo.columns and len(grupo) > 0 else ""
            email = str(grupo['Mail'].dropna().iloc[0]) if 'Mail' in grupo.columns and grupo['Mail'].notna().any() else ""
            telefono = str(grupo['Telefono'].dropna().iloc[0]) if 'Telefono' in grupo.columns and grupo['Telefono'].notna().any() else ""
            ciudad = str(grupo['Ciudad'].dropna().iloc[0]) if 'Ciudad' in grupo.columns and grupo['Ciudad'].notna().any() else ""
            pais = str(grupo['Pais'].dropna().iloc[0]) if 'Pais' in grupo.columns and grupo['Pais'].notna().any() else ""

            primera = str(grupo['Llegada'].iloc[0]) if 'Llegada' in grupo.columns and len(grupo) > 0 else ""
            ultima = str(grupo['Llegada'].iloc[-1]) if 'Llegada' in grupo.columns and len(grupo) > 0 else ""

            historial = ""
            for _, r in grupo.iterrows():
                historial += f"| {r.get('Llegada', '')} | {r.get('Salida', '')} | {r.get('Habita.', '')} | {int(r.get('Noc.', 0))} | {r.get('Origen', '')} | ${r.get('Total', 0):,.0f} | {r.get('Estado', '')} |\n"

            notas = ""
            for _, r in grupo.iterrows():
                glosa = r.get('Glosa Interna', '')
                if pd.notna(glosa) and str(glosa).strip():
                    notas += f"- {r.get('Llegada', '')}: {glosa}\n"

            contenido = f"""---
tipo: huesped
hotel: "{hotel_name}"
nombre: "{nombre}"
email: "{email}"
telefono: "{telefono}"
ciudad: "{ciudad}"
pais: "{pais}"
canal: "{canal}"
mercado: "{mercado}"
tipo_viajero: "{tipo_viajero}"
primera_visita: "{primera}"
ultima_visita: "{ultima}"
total_visitas: {visitas}
gasto_total: {gasto}
gasto_alojamiento: {gasto_aloj}
gasto_promedio: {promedio}
segmento: "{seg}"
score: {score}
tags: [huesped, {safe_name.lower()}, {seg.lower().replace(' ', '-')}, {tipo_viajero.lower()}, {mercado.lower().replace(' ', '-').replace('&', 'y')}]
---

# {nombre}
**Hotel**: {hotel_name}

## Datos de contacto
- **Email**: {email}
- **Telefono**: {telefono}
- **Ciudad**: {ciudad}
- **Pais**: {pais}

## Segmentacion
| Metrica | Valor |
|---------|-------|
| Hotel | **{hotel_name}** |
| Segmento | **{seg}** |
| Score | {score}/100 |
| Tipo viajero | {tipo_viajero} |
| Canal | {canal} |
| Mercado | {mercado} |
| Visitas | {visitas} |
| Gasto total | ${gasto:,.0f} |
| Gasto promedio | ${promedio:,.0f} |

## Historial de estadias
| Llegada | Salida | Hab. | Noches | Canal | Monto | Estado |
|---------|--------|------|--------|-------|-------|--------|
{historial}"""
            if notas:
                contenido += f"## Notas internas\n{notas}\n"

            archivo = hotel_path / f"{nombre}.md"
            archivo.write_text(contenido, encoding='utf-8')
            creados += 1

        print(f"  {hotel_name}: {creados} perfiles")
        total += creados

    print(f"  TOTAL: {total} perfiles actualizados")
    return total


def generar_csvs(all_hotels: dict[str, pd.DataFrame], hoy: pd.Timestamp):
    """Genera CSVs master y de campaña por hotel."""
    print("\n--- Generando CSVs de campaña ---")
    CAMPANAS.mkdir(exist_ok=True)

    for hotel_name, df_hotel in all_hotels.items():
        safe = hotel_name.replace(' ', '-')
        hotel_camp = CAMPANAS / safe
        hotel_camp.mkdir(exist_ok=True)

        df_act = df_hotel[~df_hotel['Estado'].isin(ESTADOS_EXCLUIR)].copy()
        df_act['Llegada_dt'] = pd.to_datetime(df_act['Llegada'], errors='coerce', dayfirst=True)
        df_act['Salida_dt'] = pd.to_datetime(df_act['Salida'], errors='coerce', dayfirst=True)

        h = df_act.groupby('Pasajero').agg(
            visitas=('Nro', 'count'),
            revenue=('Total', 'sum'),
            primera=('Llegada_dt', 'min'),
            ultima=('Salida_dt', 'max'),
            adultos_max=('Adultos', 'max'),
            menores_max=('Menores', 'max'),
            canal=('Origen', lambda x: x.mode().iloc[0] if len(x) > 0 else ''),
            mercado=('Mercado', lambda x: x.mode().iloc[0] if len(x) > 0 else ''),
            email=('Mail', 'first'),
            telefono=('Telefono', 'first'),
            ciudad=('Ciudad', 'first'),
            pais=('Pais', 'first'),
        ).reset_index()

        h['dias_desde_salida'] = (hoy - h['ultima']).dt.days
        h['hotel'] = hotel_name

        h['segmento'] = h.apply(lambda r: 'VIP' if r['visitas'] >= 3 else ('Recurrente' if r['visitas'] == 2 else 'Primera vez'), axis=1)
        h['tipo_viajero'] = h.apply(lambda r: 'Familia' if r['menores_max'] > 0 else ('Pareja' if r['adultos_max'] == 2 else ('Solo' if r['adultos_max'] == 1 else 'Grupo')), axis=1)

        # Master
        h.to_csv(hotel_camp / f'MASTER_{safe}.csv', index=False, encoding='utf-8-sig')

        # Post-estadía (checkout últimos 30 días)
        post = h[(h['dias_desde_salida'] >= 0) & (h['dias_desde_salida'] <= 30)]
        post.to_csv(hotel_camp / f'post_estadia_{safe}.csv', index=False, encoding='utf-8-sig')

        # Booking
        bk = h[h['canal'] == 'Booking.com']
        bk.to_csv(hotel_camp / f'booking_{safe}.csv', index=False, encoding='utf-8-sig')

        print(f"  {hotel_name}: MASTER={len(h)}, Post-estadía={len(post)}, Booking={len(bk)}")


def generar_csvs_dion(all_hotels: dict[str, pd.DataFrame], hoy: pd.Timestamp):
    """Genera CSVs de segmentación detallada para Hotel Dion (particulares + lotes WA)."""
    if 'Hotel Dion' not in all_hotels:
        print("  Hotel Dion no encontrado en el Excel")
        return

    print("\n--- Segmentación Hotel Dion (particulares) ---")
    df = all_hotels['Hotel Dion'].copy()

    # Solo particulares
    df = df[df['Mercado'].isin(['Directo', 'OTAs'])]
    df = df[~df['Estado'].isin(ESTADOS_EXCLUIR)]
    df['Llegada_dt'] = pd.to_datetime(df['Llegada'], errors='coerce', dayfirst=True)
    df['Salida_dt'] = pd.to_datetime(df['Salida'], errors='coerce', dayfirst=True)

    h = df.groupby('Pasajero').agg(
        visitas=('Nro', 'count'),
        revenue=('Total', 'sum'),
        primera=('Llegada_dt', 'min'),
        ultima=('Salida_dt', 'max'),
        adultos_max=('Adultos', 'max'),
        menores_max=('Menores', 'max'),
        canal=('Origen', lambda x: x.mode().iloc[0] if len(x) > 0 else ''),
        email=('Mail', 'first'),
        telefono=('Telefono', 'first'),
        ciudad=('Ciudad', 'first'),
        pais=('Pais', 'first'),
        noches_total=('Noc.', 'sum'),
    ).reset_index()

    h['dias_desde_salida'] = (hoy - h['ultima']).dt.days
    h['segmento'] = h.apply(lambda r: 'VIP' if r['visitas'] >= 3 else ('Recurrente' if r['visitas'] == 2 else 'Primera vez'), axis=1)
    h['tipo_viajero'] = h.apply(lambda r: 'Familia' if r['menores_max'] > 0 else ('Pareja' if r['adultos_max'] == 2 else ('Solo' if r['adultos_max'] == 1 else 'Grupo')), axis=1)

    out = CAMPANAS / 'Hotel-Dion'
    out.mkdir(parents=True, exist_ok=True)

    cols = ['Pasajero', 'telefono', 'email', 'ciudad', 'pais', 'canal', 'segmento',
            'tipo_viajero', 'visitas', 'revenue', 'noches_total', 'primera', 'ultima', 'dias_desde_salida']

    # Master particulares
    h[cols].sort_values('revenue', ascending=False).to_csv(out / 'PARTICULARES_MASTER.csv', index=False, encoding='utf-8-sig')

    # Por canal
    for canal_nombre, canal_filtro in [
        ('whatsapp', 'WhatsApp'),
        ('booking', 'Booking.com'),
        ('walkin', 'Walk In'),
        ('mail', 'Mail'),
        ('motor_reservas', 'Motor de reservas propio'),
    ]:
        sub = h[h['canal'] == canal_filtro].sort_values('revenue' if canal_nombre != 'whatsapp' else 'dias_desde_salida', ascending=canal_nombre != 'whatsapp')
        sub[cols].to_csv(out / f'PARTICULARES_{canal_nombre}.csv', index=False, encoding='utf-8-sig')
        print(f"  PARTICULARES_{canal_nombre}.csv: {len(sub)}")

    # Telefónico
    tel = h[h['canal'].str.contains('Telef', na=False)].sort_values('revenue', ascending=False)
    tel[cols].to_csv(out / 'PARTICULARES_telefonico.csv', index=False, encoding='utf-8-sig')
    print(f"  PARTICULARES_telefonico.csv: {len(tel)}")

    # Lotes de WhatsApp (ordenados por recencia)
    con_tel = h[h['telefono'].notna() & (h['telefono'].astype(str).str.strip() != '')]
    con_tel = con_tel.sort_values('dias_desde_salida')

    # Lote 1: últimos 30 días (seguros — te tienen agendado)
    lote1 = con_tel[con_tel['dias_desde_salida'] <= 30]
    lote1[cols].to_csv(out / 'WA_LOTE1_recientes_MANDAR_HOY.csv', index=False, encoding='utf-8-sig')

    # Lote 2: 31-90 días
    lote2 = con_tel[(con_tel['dias_desde_salida'] > 30) & (con_tel['dias_desde_salida'] <= 90)]
    lote2[cols].to_csv(out / 'WA_LOTE2_medio.csv', index=False, encoding='utf-8-sig')

    # Lote 3: 91+ días
    lote3 = con_tel[con_tel['dias_desde_salida'] > 90]
    lote3[cols].to_csv(out / 'WA_LOTE3_antiguos.csv', index=False, encoding='utf-8-sig')

    print(f"\n  Particulares Dion: {len(h)} total")
    print(f"  WA Lote 1 (recientes): {len(lote1)}")
    print(f"  WA Lote 2 (medio): {len(lote2)}")
    print(f"  WA Lote 3 (antiguos): {len(lote3)}")

    # Resumen por segmento
    print(f"\n  Por segmento:")
    for s, g in h.groupby('segmento'):
        print(f"    {s}: {len(g)} | ${g['revenue'].sum():,.0f}")

    # Contactabilidad
    con_email = h[h['email'].notna() & (h['email'].astype(str).str.strip() != '')]
    print(f"\n  Contactabilidad:")
    print(f"    Con email: {len(con_email)} ({len(con_email) / len(h) * 100:.0f}%)")
    print(f"    Con teléfono: {len(con_tel)} ({len(con_tel) / len(h) * 100:.0f}%)")


def generar_cross_hotel(all_hotels: dict[str, pd.DataFrame]):
    """Detecta huéspedes que estuvieron en más de un hotel."""
    print("\n--- Cross-hotel ---")
    all_data = pd.concat(all_hotels.values(), ignore_index=True)
    all_act = all_data[~all_data['Estado'].isin(ESTADOS_EXCLUIR)]

    cross = all_act.groupby('Pasajero')['Hotel'].nunique()
    cross_hotel = cross[cross > 1]
    print(f"  Huéspedes en más de 1 hotel: {len(cross_hotel)}")

    if len(cross_hotel) > 0:
        cross_detail = all_act[all_act['Pasajero'].isin(cross_hotel.index)]
        cross_summary = cross_detail.groupby('Pasajero').agg(
            hoteles=('Hotel', lambda x: ', '.join(x.unique())),
            visitas_total=('Nro', 'count'),
            revenue_total=('Total', 'sum'),
            email=('Mail', 'first'),
            telefono=('Telefono', 'first'),
        ).reset_index().sort_values('revenue_total', ascending=False)
        cross_summary.to_csv(CAMPANAS / 'CROSS_HOTEL_huespedes.csv', index=False, encoding='utf-8-sig')


def main():
    parser = argparse.ArgumentParser(description='Actualizar Hotel Brain completo')
    parser.add_argument('--excel', required=True, help='Path al Excel de TodoAlojamiento')
    parser.add_argument('--solo-dion', action='store_true', help='Solo procesar Hotel Dion')
    parser.add_argument('--fecha', help='Fecha de referencia YYYY-MM-DD (default: hoy)')
    parser.add_argument('--sin-perfiles', action='store_true', help='No regenerar perfiles .md (solo CSVs)')
    args = parser.parse_args()

    fecha = args.fecha or datetime.now().strftime('%Y-%m-%d')
    hoy = pd.Timestamp(fecha)

    print("=" * 50)
    print(f"ACTUALIZAR HOTEL BRAIN — {fecha}")
    print("=" * 50)

    # 1. Parsear Excel
    all_hotels = parsear_excel(args.excel)

    if args.solo_dion:
        all_hotels = {k: v for k, v in all_hotels.items() if k == 'Hotel Dion'}

    # 2. Perfiles .md
    if not args.sin_perfiles:
        crear_perfiles(all_hotels)

    # 3. CSVs de campaña
    generar_csvs(all_hotels, hoy)

    # 4. Segmentación Dion
    if 'Hotel Dion' in all_hotels or not args.solo_dion:
        generar_csvs_dion(
            {'Hotel Dion': all_hotels['Hotel Dion']} if 'Hotel Dion' in all_hotels else all_hotels,
            hoy,
        )

    # 5. Cross-hotel
    if not args.solo_dion:
        generar_cross_hotel(all_hotels)

    print("\n" + "=" * 50)
    print("BRAIN ACTUALIZADO")
    print("=" * 50)
    print(f"  Vault: {VAULT}")
    print(f"  Fecha referencia: {fecha}")
    print(f"  Abrí Obsidian y listo.")


if __name__ == '__main__':
    main()
