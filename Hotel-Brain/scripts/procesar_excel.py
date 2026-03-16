"""
Procesador de exportaciones de TodoAlojamiento -> Obsidian Vault
Convierte los XLS exportados en notas Markdown para el vault.

Uso:
    python procesar_excel.py "../00 - Inbox/reporte_reservas.xlsx"
"""

import pandas as pd
import os
import sys
import re
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path(__file__).parent.parent
HUESPEDES_PATH = VAULT_PATH / "01 - Huespedes"
RESERVAS_PATH = VAULT_PATH / "02 - Reservas"

def limpiar_nombre_archivo(nombre):
    """Limpia caracteres no validos para nombres de archivo"""
    return re.sub(r'[<>:"/\\|?*]', '', str(nombre)).strip()

def crear_nota_huesped(row, reservas_huesped):
    """Crea una nota de huesped con su historial"""
    nombre = str(row.get('nombre', row.get('Nombre', row.get('Huésped', 'Sin nombre'))))
    email = str(row.get('email', row.get('Email', row.get('E-mail', ''))))
    telefono = str(row.get('telefono', row.get('Teléfono', row.get('Tel', ''))))
    ciudad = str(row.get('ciudad', row.get('Ciudad', row.get('Localidad', ''))))
    pais = str(row.get('pais', row.get('País', 'Argentina')))

    total_visitas = len(reservas_huesped)
    gasto_total = reservas_huesped['total'].sum() if 'total' in reservas_huesped.columns else 0
    gasto_promedio = round(gasto_total / total_visitas, 0) if total_visitas > 0 else 0

    # Determinar segmento
    if total_visitas >= 3 or gasto_total > 500000:
        segmento = "VIP"
        score = 90
    elif total_visitas >= 2:
        segmento = "Recurrente"
        score = 70
    else:
        segmento = "Primera vez"
        score = 40

    # Determinar canal principal
    if 'canal' in reservas_huesped.columns:
        canal = reservas_huesped['canal'].mode().iloc[0] if len(reservas_huesped) > 0 else "Desconocido"
    else:
        canal = "Desconocido"

    historial = ""
    for _, r in reservas_huesped.iterrows():
        checkin = r.get('checkin', r.get('Check-in', ''))
        checkout = r.get('checkout', r.get('Check-out', ''))
        hab = r.get('habitacion', r.get('Habitación', ''))
        c = r.get('canal', r.get('Canal', ''))
        monto = r.get('total', r.get('Total', 0))
        historial += f"| {checkin} | {checkout} | {hab} | {c} | ${monto} |  |\n"

    contenido = f"""---
tipo: huesped
nombre: "{nombre}"
email: "{email}"
telefono: "{telefono}"
ciudad_origen: "{ciudad}"
pais: "{pais}"
canal_origen: "{canal}"
primera_visita: "{reservas_huesped.iloc[0].get('checkin', '') if len(reservas_huesped) > 0 else ''}"
ultima_visita: "{reservas_huesped.iloc[-1].get('checkin', '') if len(reservas_huesped) > 0 else ''}"
total_visitas: {total_visitas}
gasto_total: {gasto_total}
gasto_promedio: {gasto_promedio}
segmento: "{segmento}"
score: {score}
tags: [huesped, {segmento.lower().replace(' ', '-')}]
---

# {nombre}

## Datos de contacto
- Email: {email}
- Telefono: {telefono}
- Ciudad: {ciudad}
- Pais: {pais}

## Historial de estadias
| Fecha entrada | Fecha salida | Habitacion | Canal | Monto | Notas |
|--------------|-------------|------------|-------|-------|-------|
{historial}

## Segmentacion
- **Canal de origen**: {canal}
- **Segmento**: {segmento}
- **Score**: {score}/100
- **Total visitas**: {total_visitas}
- **Gasto total**: ${gasto_total:,.0f}
- **Gasto promedio**: ${gasto_promedio:,.0f}
"""
    archivo = HUESPEDES_PATH / f"{limpiar_nombre_archivo(nombre)}.md"
    archivo.write_text(contenido, encoding='utf-8')
    return nombre

def procesar_archivo(ruta_excel):
    """Procesa un archivo Excel exportado de TodoAlojamiento"""
    print(f"Leyendo: {ruta_excel}")

    # Leer todas las hojas
    xls = pd.ExcelFile(ruta_excel)
    print(f"Hojas encontradas: {xls.sheet_names}")

    for sheet in xls.sheet_names:
        df = pd.read_excel(ruta_excel, sheet_name=sheet)
        print(f"\nHoja: {sheet}")
        print(f"  Filas: {len(df)}")
        print(f"  Columnas: {list(df.columns)}")

    # Intentar leer la hoja principal
    df = pd.read_excel(ruta_excel, sheet_name=0)

    # Normalizar nombres de columnas
    col_map = {}
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if 'huesped' in col_lower or 'huésped' in col_lower or 'nombre' in col_lower:
            col_map[col] = 'nombre'
        elif 'check-in' in col_lower or 'checkin' in col_lower or 'ingreso' in col_lower or 'entrada' in col_lower:
            col_map[col] = 'checkin'
        elif 'check-out' in col_lower or 'checkout' in col_lower or 'egreso' in col_lower or 'salida' in col_lower:
            col_map[col] = 'checkout'
        elif 'habitacion' in col_lower or 'habitación' in col_lower or 'hab' in col_lower:
            col_map[col] = 'habitacion'
        elif 'canal' in col_lower or 'origen' in col_lower or 'fuente' in col_lower:
            col_map[col] = 'canal'
        elif 'total' in col_lower or 'monto' in col_lower or 'importe' in col_lower:
            col_map[col] = 'total'
        elif 'mail' in col_lower or 'email' in col_lower:
            col_map[col] = 'email'
        elif 'tel' in col_lower or 'telefono' in col_lower or 'teléfono' in col_lower:
            col_map[col] = 'telefono'
        elif 'ciudad' in col_lower or 'localidad' in col_lower:
            col_map[col] = 'ciudad'
        elif 'estado' in col_lower:
            col_map[col] = 'estado'
        elif 'noches' in col_lower:
            col_map[col] = 'noches'

    df = df.rename(columns=col_map)
    print(f"\nColumnas mapeadas: {col_map}")
    print(f"Columnas finales: {list(df.columns)}")

    # Crear notas de huespedes
    if 'nombre' in df.columns:
        huespedes = df.groupby('nombre')
        total = 0
        for nombre, grupo in huespedes:
            if pd.notna(nombre) and str(nombre).strip():
                crear_nota_huesped(grupo.iloc[0], grupo)
                total += 1
        print(f"\nHuespedes creados: {total}")
    else:
        print("\nADVERTENCIA: No se encontro columna de nombre/huesped")
        print("Columnas disponibles:", list(df.columns))
        print("\nPrimeras filas:")
        print(df.head())

    # Resumen
    print(f"\n{'='*50}")
    print(f"RESUMEN")
    print(f"{'='*50}")
    print(f"Total registros: {len(df)}")
    if 'canal' in df.columns:
        print(f"\nReservas por canal:")
        print(df['canal'].value_counts().to_string())
    if 'total' in df.columns:
        print(f"\nRevenue total: ${df['total'].sum():,.0f}")
        print(f"Ticket promedio: ${df['total'].mean():,.0f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python procesar_excel.py <archivo.xlsx>")
        print("Tambien podes dejar los archivos en '00 - Inbox/' y ejecutar sin argumentos")

        # Buscar archivos en Inbox
        inbox = VAULT_PATH / "00 - Inbox"
        archivos = list(inbox.glob("*.xlsx")) + list(inbox.glob("*.xls"))
        if archivos:
            print(f"\nArchivos encontrados en Inbox:")
            for a in archivos:
                print(f"  - {a.name}")
                procesar_archivo(str(a))
        else:
            print("\nNo hay archivos Excel en el Inbox.")
    else:
        procesar_archivo(sys.argv[1])
