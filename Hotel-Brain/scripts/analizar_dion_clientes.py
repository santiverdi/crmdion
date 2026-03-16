import pandas as pd

path = r'C:\Users\Santiago\Downloads\Listado de Reservas_11_09_2025_a_10_03_2026.xlsx'
df_raw = pd.read_excel(path, header=None)

header_row = 6759
df = df_raw.iloc[header_row+1:].copy()
df.columns = df_raw.iloc[header_row].values
df = df[df.iloc[:,0] != 'TOTALES:'].dropna(subset=[df.columns[0]])
df = df[~df.iloc[:,0].astype(str).str.startswith('Hotel')]
df = df[df.iloc[:,0] != 'Nro']

for col in ['Total', 'Noc. V', 'Noc.', 'Adultos']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

print('HOTEL DION - Tipo de cliente')
print('='*60)

print('\nMERCADO:')
for m, g in df.groupby('Mercado'):
    print(f'  {m}: {len(g)} reservas | ${g["Total"].sum():,.0f}')

print('\nORIGEN:')
for o, g in df.groupby('Origen'):
    print(f'  {o}: {len(g)} reservas | ${g["Total"].sum():,.0f}')

# Empresa field
emp_col = None
for c in df.columns:
    if 'mpresa' in str(c):
        emp_col = c
        break

if emp_col:
    empresas = df[df[emp_col].notna() & (df[emp_col].astype(str).str.strip() != '')]
    print(f'\n{"="*60}')
    print(f'CAMPO EMPRESA: {len(empresas)} reservas con empresa asignada')
    if len(empresas) > 0:
        print('\nEmpresas/Agencias:')
        for e, g in empresas.groupby(emp_col):
            print(f'  {str(e):45s} | {len(g)} res | ${g["Total"].sum():,.0f}')

# Tour & Travel
print(f'\n{"="*60}')
print('TOUR & TRAVEL (agencias):')
tt = df[df['Mercado'] == 'Tour & Travel']
print(f'Total: {len(tt)} reservas | ${tt["Total"].sum():,.0f}')
if len(tt) > 0:
    col_group = emp_col if (emp_col and tt[emp_col].notna().any()) else 'Pasajero'
    for e, g in tt.groupby(col_group):
        if str(e).strip():
            print(f'  {str(e):45s} | {len(g)} res | ${g["Total"].sum():,.0f}')

# Corporativo
print(f'\n{"="*60}')
print('CORPORATIVO:')
corp = df[df['Mercado'] == 'Corporativo']
print(f'Total: {len(corp)} reservas | ${corp["Total"].sum():,.0f}')
if len(corp) > 0:
    col_group = emp_col if (emp_col and corp[emp_col].notna().any()) else 'Pasajero'
    for e, g in corp.groupby(col_group):
        if str(e).strip():
            print(f'  {str(e):45s} | {len(g)} res | ${g["Total"].sum():,.0f}')

# Glosas internas con info util
print(f'\n{"="*60}')
print('NOTAS INTERNAS (glosas con info de empresas/agencias):')
glosas = df[df['Glosa Interna'].notna() & (df['Glosa Interna'].astype(str).str.strip() != '')]
for _, r in glosas.iterrows():
    glosa = str(r['Glosa Interna']).strip()
    if len(glosa) > 3:
        print(f'  {str(r["Pasajero"]):35s} | {r["Mercado"]:15s} | {r["Origen"]:20s} | {glosa[:70]}')
