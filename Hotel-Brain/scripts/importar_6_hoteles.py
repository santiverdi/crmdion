"""
Importador TodoAlojamiento -> Obsidian Vault
6 Hoteles: Prince, Kings, VIPS, America, Valles, Dion
Foco marketing: Hotel Dion
"""

import pandas as pd
import re
from pathlib import Path

VAULT = Path(r'C:\Users\Santiago\Desktop\HOTEL CRM-BOT-OBS\Hotel-Brain')
EXCEL = Path(r'C:\Users\Santiago\Downloads\Listado de Reservas_11_09_2025_a_10_03_2026.xlsx')

def limpiar(nombre):
    if pd.isna(nombre): return "Sin nombre"
    return re.sub(r'[<>:"/\\|?*]', '', str(nombre)).strip()

def segmentar(visitas, gasto, adultos, menores):
    if visitas >= 3 or gasto > 800000:
        seg, score = "VIP", 90
    elif visitas >= 2:
        seg, score = "Recurrente", 70
    else:
        seg, score = "Primera vez", 40
    if menores > 0: tipo = "Familia"
    elif adultos == 2: tipo = "Pareja"
    elif adultos == 1: tipo = "Solo"
    else: tipo = "Grupo"
    return seg, score, tipo

# ============================================
# PARSE ALL 6 HOTELS
# ============================================
print("Leyendo Excel...")
df_raw = pd.read_excel(EXCEL, header=None)

separators = {
    2: 'Hotel Prince',
    1063: 'Hotel Kings',
    2852: 'Hotel VIPS',
    4298: 'Hotel America',
    4928: 'Hotel Valles',
    6757: 'Hotel Dion'
}

sep_rows = sorted(separators.keys())
all_hotels = {}

for idx, start_row in enumerate(sep_rows):
    hotel_name = separators[start_row]
    header_row = start_row + 2
    end_row = sep_rows[idx + 1] if idx + 1 < len(sep_rows) else len(df_raw)

    section = df_raw.iloc[header_row+1:end_row].copy()
    section.columns = df_raw.iloc[header_row].values
    section = section[section.iloc[:,0] != 'TOTALES:']
    section = section.dropna(subset=[section.columns[0]])
    section = section[~section.iloc[:,0].astype(str).str.startswith('Hotel')]
    section = section[section.iloc[:,0] != 'Nro']
    section['Hotel'] = hotel_name

    for col in ['Total', 'Total Alojamiento', 'T. Promedio', 'Adultos', 'Menores', 'Infantes', 'Noc.', 'Noc. V', 'Saldo']:
        if col in section.columns:
            section[col] = pd.to_numeric(section[col], errors='coerce').fillna(0)

    all_hotels[hotel_name] = section
    print(f"  {hotel_name}: {len(section)} reservas")

all_data = pd.concat(all_hotels.values(), ignore_index=True)
print(f"\nTotal: {len(all_data)} reservas de 6 hoteles")

# ============================================
# CREATE HOTEL FOLDERS
# ============================================
for hotel_name, df_hotel in all_hotels.items():
    safe_name = hotel_name.replace(' ', '-')
    hotel_path = VAULT / "01 - Huespedes" / safe_name
    hotel_path.mkdir(parents=True, exist_ok=True)

    df_activas = df_hotel[~df_hotel['Estado'].isin([
        'Cancelada por el pasajero', 'Cancelada por falta de respuesta',
        'No Show', 'Pago Rechazado'
    ])]

    # Create guest profiles
    huespedes_group = df_activas.groupby('Pasajero')
    total_creados = 0

    for nombre_raw, grupo in huespedes_group:
        nombre = limpiar(nombre_raw)
        if not nombre or nombre == "Sin nombre":
            continue

        grupo = grupo.sort_values('Llegada') if 'Llegada' in grupo.columns else grupo
        visitas = len(grupo)
        gasto = grupo['Total'].sum()
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
            historial += f"| {r.get('Llegada','')} | {r.get('Salida','')} | {r.get('Habita.','')} | {int(r.get('Noc.',0))} | {r.get('Origen','')} | ${r.get('Total',0):,.0f} | {r.get('Estado','')} |\n"

        notas = ""
        for _, r in grupo.iterrows():
            glosa = r.get('Glosa Interna', '')
            if pd.notna(glosa) and str(glosa).strip():
                notas += f"- {r.get('Llegada','')}: {glosa}\n"

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
gasto_promedio: {promedio}
segmento: "{seg}"
score: {score}
tags: [huesped, {safe_name.lower()}, {seg.lower().replace(' ','-')}, {tipo_viajero.lower()}, {mercado.lower().replace(' ','-').replace('&','y')}]
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
{historial}
"""
        if notas:
            contenido += f"## Notas internas\n{notas}\n"

        archivo = hotel_path / f"{nombre}.md"
        archivo.write_text(contenido, encoding='utf-8')
        total_creados += 1

    print(f"  {hotel_name}: {total_creados} perfiles creados")

# ============================================
# EXPORT CSVs PER HOTEL
# ============================================
print("\nExportando CSVs por hotel...")
campanas = VAULT / "07 - Campañas"
campanas.mkdir(exist_ok=True)

hoy = pd.Timestamp('2026-03-10')

for hotel_name, df_hotel in all_hotels.items():
    safe = hotel_name.replace(' ', '-')
    hotel_camp = campanas / safe
    hotel_camp.mkdir(exist_ok=True)

    df_act = df_hotel[~df_hotel['Estado'].isin([
        'Cancelada por el pasajero', 'Cancelada por falta de respuesta',
        'No Show', 'Pago Rechazado'
    ])]

    df_act = df_act.copy()
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

    def seg(row):
        if row['visitas'] >= 3: return 'VIP'
        elif row['visitas'] == 2: return 'Recurrente'
        else: return 'Primera vez'
    def tipo(row):
        if row['menores_max'] > 0: return 'Familia'
        elif row['adultos_max'] == 2: return 'Pareja'
        elif row['adultos_max'] == 1: return 'Solo'
        else: return 'Grupo'

    h['segmento'] = h.apply(seg, axis=1)
    h['tipo_viajero'] = h.apply(tipo, axis=1)

    # Master CSV per hotel
    h.to_csv(hotel_camp / f'MASTER_{safe}.csv', index=False, encoding='utf-8-sig')

    # Post-estadia
    post = h[(h['dias_desde_salida'] >= 0) & (h['dias_desde_salida'] <= 30)]
    post.to_csv(hotel_camp / f'post_estadia_{safe}.csv', index=False, encoding='utf-8-sig')

    # Booking
    bk = h[h['canal'] == 'Booking.com']
    bk.to_csv(hotel_camp / f'booking_{safe}.csv', index=False, encoding='utf-8-sig')

    print(f"  {hotel_name}: MASTER={len(h)}, Post-estadia={len(post)}, Booking={len(bk)}")

# ============================================
# MASTER TOTAL (6 hoteles)
# ============================================
print("\nExportando MASTER total...")
all_activas = all_data[~all_data['Estado'].isin([
    'Cancelada por el pasajero', 'Cancelada por falta de respuesta',
    'No Show', 'Pago Rechazado'
])]

all_activas_c = all_activas.copy()
all_activas_c['Llegada_dt'] = pd.to_datetime(all_activas_c['Llegada'], errors='coerce', dayfirst=True)
all_activas_c['Salida_dt'] = pd.to_datetime(all_activas_c['Salida'], errors='coerce', dayfirst=True)

master = all_activas_c.groupby(['Hotel', 'Pasajero']).agg(
    visitas=('Nro', 'count'),
    revenue=('Total', 'sum'),
    primera=('Llegada_dt', 'min'),
    ultima=('Salida_dt', 'max'),
    canal=('Origen', lambda x: x.mode().iloc[0] if len(x) > 0 else ''),
    email=('Mail', 'first'),
    telefono=('Telefono', 'first'),
    ciudad=('Ciudad', 'first'),
).reset_index()

master.to_csv(campanas / 'MASTER_6_HOTELES.csv', index=False, encoding='utf-8-sig')
print(f"MASTER total: {len(master)} registros (huesped x hotel)")

# Cross-hotel guests (estuvieron en mas de 1 hotel)
cross = all_activas_c.groupby('Pasajero')['Hotel'].nunique()
cross_hotel = cross[cross > 1]
print(f"\nHuespedes que estuvieron en MAS DE 1 hotel: {len(cross_hotel)}")

if len(cross_hotel) > 0:
    cross_detail = all_activas_c[all_activas_c['Pasajero'].isin(cross_hotel.index)]
    cross_summary = cross_detail.groupby('Pasajero').agg(
        hoteles=('Hotel', lambda x: ', '.join(x.unique())),
        visitas_total=('Nro', 'count'),
        revenue_total=('Total', 'sum'),
        email=('Mail', 'first'),
        telefono=('Telefono', 'first'),
    ).reset_index().sort_values('revenue_total', ascending=False)
    cross_summary.to_csv(campanas / 'CROSS_HOTEL_huespedes.csv', index=False, encoding='utf-8-sig')
    print(f"Exportado: CROSS_HOTEL_huespedes.csv ({len(cross_summary)} personas)")
    print("\nTop 10 cross-hotel:")
    for _, r in cross_summary.head(10).iterrows():
        print(f"  {r['Pasajero']} | {r['hoteles']} | {int(r['visitas_total'])} visitas | ${r['revenue_total']:,.0f}")

print("\n" + "="*50)
print("IMPORTACION 6 HOTELES COMPLETA")
print("="*50)
