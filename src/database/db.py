"""Conexión SQLite para leads del cualificador."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "leads.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db() -> sqlite3.Connection:
    """Retorna conexión a la DB, creando tablas si no existen."""
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")

    # Crear tablas si no existen
    schema = SCHEMA_PATH.read_text(encoding='utf-8')
    db.executescript(schema)

    return db


def guardar_lead(data: dict) -> int:
    """Guarda un lead y retorna su ID."""
    db = get_db()
    cursor = db.execute(
        """INSERT INTO leads (nombre, telefono, email, checkin, checkout,
           adultos, menores, tipo_habitacion, mensaje, utm_source, utm_campaign)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data['nombre'],
            data['telefono'],
            data.get('email', ''),
            data['checkin'],
            data['checkout'],
            data.get('adultos', 1),
            data.get('menores', 0),
            data['tipo_habitacion'],
            data.get('mensaje', ''),
            data.get('utm_source', ''),
            data.get('utm_campaign', ''),
        )
    )
    db.commit()
    lead_id = cursor.lastrowid
    db.close()
    return lead_id


def actualizar_estado(lead_id: int, estado: str, notas: str = ""):
    """Actualiza el estado de un lead."""
    db = get_db()
    ahora = datetime.now().isoformat()

    campos_fecha = {
        'contactado': 'contactado_at',
        'reservado': 'reservado_at',
    }

    query = "UPDATE leads SET estado = ?"
    params = [estado]

    if estado in campos_fecha:
        query += f", {campos_fecha[estado]} = ?"
        params.append(ahora)

    if notas:
        query += ", notas = ?"
        params.append(notas)

    query += " WHERE id = ?"
    params.append(lead_id)

    db.execute(query, params)
    db.commit()
    db.close()


def listar_leads(estado: str = None, limite: int = 50) -> list[dict]:
    """Lista leads, opcionalmente filtrados por estado."""
    db = get_db()

    if estado:
        rows = db.execute(
            "SELECT * FROM leads WHERE estado = ? ORDER BY created_at DESC LIMIT ?",
            (estado, limite)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM leads ORDER BY created_at DESC LIMIT ?",
            (limite,)
        ).fetchall()

    db.close()
    return [dict(r) for r in rows]


def stats_leads() -> dict:
    """Estadísticas de leads."""
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    por_estado = {}
    for row in db.execute("SELECT estado, COUNT(*) as n FROM leads GROUP BY estado"):
        por_estado[row['estado']] = row['n']
    db.close()
    return {'total': total, 'por_estado': por_estado}
