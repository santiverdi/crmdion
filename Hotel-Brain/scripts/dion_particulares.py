import pandas as pd
from pathlib import Path

path = r'C:\Users\Santiago\Downloads\Listado de Reservas_11_09_2025_a_10_03_2026.xlsx'
df_raw = pd.read_excel(path, header=None)

header_row = 6759
df = df_raw.iloc[header_row+1:].copy()
df.columns = df_raw.iloc[header_row].values
df = df[df.iloc[:,0] != 'TOTALES:'].dropna(subset=[df.columns[0]])
df = df[~df.iloc[:,0].astype(str).str.startswith('Hotel')]
df = df[df.iloc[:,0] != 'Nro']

for col in ['Total', 'Adultos', 'Menores', 'Noc.', 'Noc. V']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# SOLO particulares: Directo + OTAs (sin Tour & Travel ni Corporativo)
df = df[df['Mercado'].isin(['Directo', 'OTAs'])]

# Solo activas
df = df[~df['Estado'].isin(['Cancelada por el pasajero', 'Cancelada por falta de respuesta', 'No Show', 'Pago Rechazado'])]

df['Llegada_dt'] = pd.to_datetime(df['Llegada'], errors='coerce', dayfirst=True)
df['Salida_dt'] = pd.to_datetime(df['Salida'], errors='coerce', dayfirst=True)
hoy = pd.Timestamp('2026-03-10')

print(f'HOTEL DION - Solo particulares (Directo + OTAs)')
print(f'Reservas: {len(df)}')
print(f'\nPor origen:')
for o, g in df.groupby('Origen'):
    print(f'  {o}: {len(g)} reservas | ${g["Total"].sum():,.0f}')

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

print(f'\nParticulares unicos: {len(h)}')
print(f'\nPor segmento:')
for s, g in h.groupby('segmento'):
    print(f'  {s}: {len(g)} | ${g["revenue"].sum():,.0f}')
print(f'\nPor canal:')
for c, g in h.groupby('canal'):
    print(f'  {c}: {len(g)} | ${g["revenue"].sum():,.0f}')
print(f'\nPor tipo viajero:')
for t, g in h.groupby('tipo_viajero'):
    print(f'  {t}: {len(g)}')

con_email = h[h['email'].notna() & (h['email'].astype(str).str.strip() != '')]
con_tel = h[h['telefono'].notna() & (h['telefono'].astype(str).str.strip() != '')]
print(f'\nContactabilidad:')
print(f'  Con email: {len(con_email)} ({len(con_email)/len(h)*100:.0f}%)')
print(f'  Con telefono: {len(con_tel)} ({len(con_tel)/len(h)*100:.0f}%)')

# Export por canal
out = Path(r'C:\Users\Santiago\Desktop\HOTEL CRM-BOT-OBS\Hotel-Brain') / '07 - Campañas' / 'Hotel-Dion'
out.mkdir(parents=True, exist_ok=True)
cols = ['Pasajero','telefono','email','ciudad','pais','canal','segmento','tipo_viajero','visitas','revenue','noches_total','primera','ultima','dias_desde_salida']

# WhatsApp
wa = h[h['canal'] == 'WhatsApp'].sort_values('dias_desde_salida')
wa[cols].to_csv(out / 'PARTICULARES_whatsapp.csv', index=False, encoding='utf-8-sig')

# Booking
bk = h[h['canal'] == 'Booking.com'].sort_values('revenue', ascending=False)
bk[cols].to_csv(out / 'PARTICULARES_booking.csv', index=False, encoding='utf-8-sig')

# Walk In
wi = h[h['canal'] == 'Walk In'].sort_values('revenue', ascending=False)
wi[cols].to_csv(out / 'PARTICULARES_walkin.csv', index=False, encoding='utf-8-sig')

# Telefonico
tel = h[h['canal'].str.contains('Telef', na=False)].sort_values('revenue', ascending=False)
tel[cols].to_csv(out / 'PARTICULARES_telefonico.csv', index=False, encoding='utf-8-sig')

# Mail
ml = h[h['canal'] == 'Mail'].sort_values('revenue', ascending=False)
ml[cols].to_csv(out / 'PARTICULARES_mail.csv', index=False, encoding='utf-8-sig')

# Motor de reservas
mr = h[h['canal'] == 'Motor de reservas propio'].sort_values('revenue', ascending=False)
mr[cols].to_csv(out / 'PARTICULARES_motor_reservas.csv', index=False, encoding='utf-8-sig')

# MASTER particulares
h[cols].sort_values('revenue', ascending=False).to_csv(out / 'PARTICULARES_MASTER.csv', index=False, encoding='utf-8-sig')

print(f'\nCSVs exportados:')
print(f'  PARTICULARES_MASTER.csv: {len(h)} contactos')
print(f'  PARTICULARES_whatsapp.csv: {len(wa)}')
print(f'  PARTICULARES_booking.csv: {len(bk)}')
print(f'  PARTICULARES_walkin.csv: {len(wi)}')
print(f'  PARTICULARES_telefonico.csv: {len(tel)}')
print(f'  PARTICULARES_mail.csv: {len(ml)}')
print(f'  PARTICULARES_motor_reservas.csv: {len(mr)}')
