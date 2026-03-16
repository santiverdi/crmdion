"""
Importador TodoAlojamiento -> Obsidian Vault
Hotel Prince Hotel - Mar del Plata
"""

import pandas as pd
import os
import re
from pathlib import Path
from datetime import datetime

VAULT = Path(r'C:\Users\Santiago\Desktop\HOTEL CRM-BOT-OBS\Hotel-Brain')
HUESPEDES = VAULT / "01 - Huespedes"
RESERVAS = VAULT / "02 - Reservas"
ANALYTICS = VAULT / "06 - Analytics"
EXCEL = Path(r'C:\Users\Santiago\Downloads\Listado de Reservas_11_09_2025_a_10_03_2026.xlsx')

def limpiar(nombre):
    if pd.isna(nombre): return "Sin nombre"
    return re.sub(r'[<>:"/\\|?*]', '', str(nombre)).strip()

def segmentar(visitas, gasto, adultos, menores):
    """Asigna segmento y score"""
    if visitas >= 3 or gasto > 800000:
        seg, score = "VIP", 90
    elif visitas >= 2:
        seg, score = "Recurrente", 70
    else:
        seg, score = "Primera vez", 40

    # Tipo de viajero
    if menores > 0:
        tipo = "Familia"
    elif adultos == 2:
        tipo = "Pareja"
    elif adultos == 1:
        tipo = "Solo"
    else:
        tipo = "Grupo"

    return seg, score, tipo

print("Leyendo Excel...")
df = pd.read_excel(EXCEL, header=4)
df = df[df.iloc[:,0] != 'TOTALES:'].dropna(subset=[df.columns[0]])

# Limpiar datos
for col in ['Total Alojamiento', 'T. Promedio', 'Total', 'Saldo', 'Adultos', 'Menores', 'Infantes', 'Noc.', 'Noc. V', 'Comisión', '% Comisión']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Filtrar canceladas para huespedes (pero las guardamos para analytics)
df_activas = df[~df['Estado'].isin(['Cancelada por el pasajero', 'Cancelada por falta de respuesta', 'No Show', 'Pago Rechazado'])]

print(f"Total reservas: {len(df)}")
print(f"Reservas activas: {len(df_activas)}")
print(f"Pasajeros unicos (activas): {df_activas['Pasajero'].nunique()}")

# ============================================
# CREAR NOTAS DE HUESPEDES
# ============================================
print("\nCreando perfiles de huespedes...")
HUESPEDES.mkdir(exist_ok=True)

huespedes_group = df_activas.groupby('Pasajero')
total_creados = 0

for nombre_raw, grupo in huespedes_group:
    nombre = limpiar(nombre_raw)
    if not nombre or nombre == "Sin nombre":
        continue

    grupo = grupo.sort_values('Llegada')
    visitas = len(grupo)
    gasto = grupo['Total'].sum()
    gasto_aloj = grupo['Total Alojamiento'].sum()
    promedio = round(gasto / visitas, 0) if visitas > 0 else 0
    adultos_max = int(grupo['Adultos'].max())
    menores_max = int(grupo['Menores'].max())

    seg, score, tipo_viajero = segmentar(visitas, gasto, adultos_max, menores_max)

    # Canal mas frecuente
    canal = grupo['Origen'].mode().iloc[0] if len(grupo) > 0 else "Desconocido"
    mercado = grupo['Mercado'].mode().iloc[0] if len(grupo) > 0 else "Desconocido"

    # Datos de contacto
    email = str(grupo['Mail'].dropna().iloc[0]) if grupo['Mail'].notna().any() else ""
    telefono = str(grupo['Telefono'].dropna().iloc[0]) if grupo['Telefono'].notna().any() else ""
    ciudad = str(grupo['Ciudad'].dropna().iloc[0]) if 'Ciudad' in grupo.columns and grupo['Ciudad'].notna().any() else ""
    pais = str(grupo['Pais'].dropna().iloc[0]) if 'Pais' in grupo.columns and grupo['Pais'].notna().any() else "Argentina"

    primera = str(grupo['Llegada'].iloc[0]) if len(grupo) > 0 else ""
    ultima = str(grupo['Llegada'].iloc[-1]) if len(grupo) > 0 else ""

    # Historial
    historial = ""
    for _, r in grupo.iterrows():
        llegada = str(r.get('Llegada', ''))
        salida = str(r.get('Salida', ''))
        hab = str(r.get('Habita.', ''))
        orig = str(r.get('Origen', ''))
        monto = r.get('Total', 0)
        noches = int(r.get('Noc.', 0))
        estado = str(r.get('Estado', ''))
        historial += f"| {llegada} | {salida} | {hab} | {noches} | {orig} | ${monto:,.0f} | {estado} |\n"

    # Glosas/notas internas
    notas_internas = ""
    for _, r in grupo.iterrows():
        glosa = r.get('Glosa Interna', '')
        if pd.notna(glosa) and str(glosa).strip():
            notas_internas += f"- {r.get('Llegada', '')}: {glosa}\n"

    contenido = f"""---
tipo: huesped
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
tags: [huesped, {seg.lower().replace(' ', '-')}, {tipo_viajero.lower()}, {mercado.lower().replace(' ', '-').replace('&', 'y')}]
---

# {nombre}

## Datos de contacto
- **Email**: {email}
- **Telefono**: {telefono}
- **Ciudad**: {ciudad}
- **Pais**: {pais}

## Segmentacion
| Metrica | Valor |
|---------|-------|
| Segmento | **{seg}** |
| Score | {score}/100 |
| Tipo viajero | {tipo_viajero} |
| Canal principal | {canal} |
| Mercado | {mercado} |
| Total visitas | {visitas} |
| Gasto total | ${gasto:,.0f} |
| Gasto promedio | ${promedio:,.0f} |

## Historial de estadias
| Llegada | Salida | Hab. | Noches | Canal | Monto | Estado |
|---------|--------|------|--------|-------|-------|--------|
{historial}
"""
    if notas_internas:
        contenido += f"""## Notas internas
{notas_internas}
"""

    archivo = HUESPEDES / f"{nombre}.md"
    archivo.write_text(contenido, encoding='utf-8')
    total_creados += 1

print(f"Perfiles creados: {total_creados}")

# ============================================
# CREAR INDEX DE HUESPEDES
# ============================================
index_content = """# Huespedes - Base de datos

## Todos los huespedes
```dataview
TABLE
  segmento as "Segmento",
  tipo_viajero as "Tipo",
  total_visitas as "Visitas",
  gasto_total as "Gasto Total",
  canal as "Canal",
  ciudad as "Ciudad",
  ultima_visita as "Ultima visita"
FROM "01 - Huespedes"
WHERE tipo = "huesped"
SORT gasto_total DESC
```

## VIPs (3+ visitas o alto gasto)
```dataview
TABLE
  total_visitas as "Visitas",
  gasto_total as "Gasto",
  canal as "Canal",
  telefono as "Tel"
FROM "01 - Huespedes"
WHERE segmento = "VIP"
SORT gasto_total DESC
```

## Recurrentes
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", canal as "Canal"
FROM "01 - Huespedes"
WHERE segmento = "Recurrente"
SORT gasto_total DESC
```

## Con email (para campanas)
```dataview
TABLE email as "Email", segmento as "Seg", gasto_total as "Gasto"
FROM "01 - Huespedes"
WHERE email != "" AND tipo = "huesped"
SORT gasto_total DESC
```

## Familias
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", ciudad as "Ciudad"
FROM "01 - Huespedes"
WHERE tipo_viajero = "Familia"
SORT gasto_total DESC
```

## Por ciudad
```dataview
TABLE length(rows) as "Huespedes", sum(rows.gasto_total) as "Revenue"
FROM "01 - Huespedes"
WHERE tipo = "huesped"
GROUP BY ciudad
SORT length(rows) DESC
```
"""
(HUESPEDES / "Index.md").write_text(index_content, encoding='utf-8')

# ============================================
# ANALYTICS COMPLETO
# ============================================
print("\nGenerando analytics...")

# Revenue por canal
rev_canal = df_activas.groupby('Origen').agg(
    reservas=('Nro', 'count'),
    revenue=('Total', 'sum'),
    noches=('Noc.', 'sum'),
    promedio=('Total', 'mean')
).sort_values('revenue', ascending=False)

# Revenue por mercado
rev_mercado = df_activas.groupby('Mercado').agg(
    reservas=('Nro', 'count'),
    revenue=('Total', 'sum'),
    promedio=('Total', 'mean')
).sort_values('revenue', ascending=False)

# Revenue por mes
df_activas_copy = df_activas.copy()
df_activas_copy['Llegada_dt'] = pd.to_datetime(df_activas_copy['Llegada'], errors='coerce', dayfirst=True)
df_activas_copy['Mes'] = df_activas_copy['Llegada_dt'].dt.strftime('%Y-%m')

rev_mes = df_activas_copy.groupby('Mes').agg(
    reservas=('Nro', 'count'),
    revenue=('Total', 'sum'),
    noches=('Noc. V', 'sum'),
    adultos=('Adultos', 'sum')
).sort_index()

# Ciudades top
top_ciudades = df_activas['Ciudad'].value_counts().head(20)

analytics_md = f"""# Analytics - Hotel Prince

> Periodo: Sep 2025 - Mar 2026 | {len(df)} reservas totales | {len(df_activas)} activas

## Resumen ejecutivo
| Metrica | Valor |
|---------|-------|
| Reservas totales | {len(df):,} |
| Reservas activas | {len(df_activas):,} |
| Cancelaciones | {len(df) - len(df_activas):,} ({(len(df)-len(df_activas))/len(df)*100:.1f}%) |
| Revenue total | ${df_activas['Total'].sum():,.0f} ARS |
| Revenue alojamiento | ${df_activas['Total Alojamiento'].sum():,.0f} ARS |
| Ticket promedio | ${df_activas['Total'].mean():,.0f} ARS |
| Tarifa promedio/noche | ${df_activas['T. Promedio'].mean():,.0f} ARS |
| Pasajeros unicos | {df_activas['Pasajero'].nunique():,} |
| Total noches vendidas | {df_activas['Noc. V'].sum():,.0f} |
| Promedio noches/reserva | {df_activas['Noc.'].mean():.1f} |

## Revenue por mercado
| Mercado | Reservas | Revenue | Ticket Promedio |
|---------|----------|---------|-----------------|
"""

for mercado, row in rev_mercado.iterrows():
    analytics_md += f"| {mercado} | {int(row['reservas']):,} | ${row['revenue']:,.0f} | ${row['promedio']:,.0f} |\n"

analytics_md += f"""
## Revenue por canal (origen)
| Canal | Reservas | Revenue | Ticket Promedio |
|-------|----------|---------|-----------------|
"""

for origen, row in rev_canal.iterrows():
    analytics_md += f"| {origen} | {int(row['reservas']):,} | ${row['revenue']:,.0f} | ${row['promedio']:,.0f} |\n"

analytics_md += f"""
## Revenue por mes
| Mes | Reservas | Revenue | Noches vendidas |
|-----|----------|---------|-----------------|
"""

for mes, row in rev_mes.iterrows():
    analytics_md += f"| {mes} | {int(row['reservas']):,} | ${row['revenue']:,.0f} | {int(row['noches']):,} |\n"

analytics_md += f"""
## Top 20 ciudades de origen
| Ciudad | Reservas |
|--------|----------|
"""

for ciudad, count in top_ciudades.items():
    analytics_md += f"| {ciudad} | {count} |\n"

analytics_md += f"""
## Estado de reservas
| Estado | Cantidad | % |
|--------|----------|---|
"""

for estado, count in df['Estado'].value_counts().items():
    analytics_md += f"| {estado} | {count:,} | {count/len(df)*100:.1f}% |\n"

analytics_md += """
## Queries Dataview en vivo

### Huespedes VIP
```dataview
TABLE total_visitas as "Visitas", gasto_total as "Gasto", canal as "Canal", telefono as "Tel"
FROM "01 - Huespedes"
WHERE segmento = "VIP"
SORT gasto_total DESC
LIMIT 30
```

### Revenue por canal (vivo)
```dataview
TABLE
  length(rows) as "Reservas",
  sum(rows.gasto_total) as "Revenue Total"
FROM "01 - Huespedes"
WHERE tipo = "huesped"
GROUP BY mercado
SORT sum(rows.gasto_total) DESC
```
"""

(ANALYTICS / "Index.md").write_text(analytics_md, encoding='utf-8')

# ============================================
# RESERVAS INDEX
# ============================================
reservas_index = """# Reservas

## Pipeline activo
```dataview
TABLE
  pasajero as "Pasajero",
  llegada as "Llegada",
  salida as "Salida",
  noches as "Noches",
  canal as "Canal",
  total as "Total"
FROM "02 - Reservas"
WHERE tipo = "reserva"
SORT llegada DESC
LIMIT 50
```
"""
RESERVAS.mkdir(exist_ok=True)
(RESERVAS / "Index.md").write_text(reservas_index, encoding='utf-8')

print("\n" + "="*50)
print("IMPORTACION COMPLETA")
print("="*50)
print(f"Perfiles de huespedes: {total_creados}")
print(f"Analytics generado: SI")
print(f"Vault: {VAULT}")
print(f"\nAbri '{VAULT}' como vault en Obsidian!")
