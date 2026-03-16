"""Servidor de la landing page + API de leads para Hotel Dion.

Uso:
    python src/landing/server.py
    python src/landing/server.py --port 8080

Requiere:
    pip install fastapi uvicorn python-dotenv
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, field_validator

# Setup paths
ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / "config" / ".env")

sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db import actualizar_estado, guardar_lead, listar_leads, stats_leads
from utils.notify import notificar_conserje

app = FastAPI(title="Hotel Dion - Lead Qualifier")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---

class LeadInput(BaseModel):
    nombre: str
    telefono: str
    email: str = ""
    checkin: str
    checkout: str
    adultos: int = 1
    menores: int = 0
    tipo_habitacion: str
    mensaje: str = ""
    utm_source: str = ""
    utm_campaign: str = ""

    @field_validator('nombre')
    @classmethod
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('Nombre requerido')
        return v.strip()

    @field_validator('telefono')
    @classmethod
    def telefono_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('Teléfono requerido')
        return v.strip()

    @field_validator('checkin', 'checkout')
    @classmethod
    def fecha_valida(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Fecha inválida, usar formato YYYY-MM-DD')
        return v


class EstadoUpdate(BaseModel):
    estado: str
    notas: str = ""

    @field_validator('estado')
    @classmethod
    def estado_valido(cls, v):
        validos = {'nuevo', 'contactado', 'reservado', 'perdido'}
        if v not in validos:
            raise ValueError(f'Estado debe ser uno de: {validos}')
        return v


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Sirve la landing page."""
    html_path = Path(__file__).parent / "page.html"
    return HTMLResponse(html_path.read_text(encoding='utf-8'))


@app.post("/api/lead")
async def recibir_lead(lead: LeadInput):
    """Recibe un lead del formulario y notifica al conserje."""
    data = lead.model_dump()
    lead_id = guardar_lead(data)
    data['id'] = lead_id

    # Notificar al conserje (async en background sería ideal, pero funciona sync)
    notificado = notificar_conserje(data)

    return JSONResponse(
        {"ok": True, "lead_id": lead_id, "notificado": notificado},
        status_code=201,
    )


@app.get("/api/leads")
async def ver_leads(estado: str = None, limite: int = 50):
    """Lista leads (para el panel del conserje)."""
    return listar_leads(estado=estado, limite=limite)


@app.patch("/api/leads/{lead_id}")
async def update_lead(lead_id: int, update: EstadoUpdate):
    """Actualiza el estado de un lead."""
    actualizar_estado(lead_id, update.estado, update.notas)
    return {"ok": True}


@app.get("/api/stats")
async def ver_stats():
    """Estadísticas de leads."""
    return stats_leads()


@app.get("/panel", response_class=HTMLResponse)
async def panel_conserje():
    """Panel simple para que el conserje vea y gestione leads."""
    leads = listar_leads(limite=100)
    rows = ""
    for l in leads:
        estado_class = {
            'nuevo': '#e74c3c',
            'contactado': '#f39c12',
            'reservado': '#27ae60',
            'perdido': '#95a5a6',
        }.get(l['estado'], '#666')

        rows += f"""
        <tr>
            <td>{l['id']}</td>
            <td><strong>{l['nombre']}</strong><br><small>{l['telefono']}</small></td>
            <td>{l['checkin']}<br>→ {l['checkout']}</td>
            <td>{l['adultos']}A {'+' + str(l['menores']) + 'M' if l['menores'] else ''}</td>
            <td>{l['tipo_habitacion']}</td>
            <td><span style="background:{estado_class};color:white;padding:2px 8px;border-radius:4px;font-size:0.8em">{l['estado']}</span></td>
            <td><small>{l['created_at'][:16] if l['created_at'] else ''}</small></td>
            <td>
                <select onchange="cambiarEstado({l['id']}, this.value)" style="font-size:0.85em;padding:4px">
                    <option value="">Cambiar...</option>
                    <option value="contactado">Contactado</option>
                    <option value="reservado">Reservado</option>
                    <option value="perdido">Perdido</option>
                </select>
            </td>
        </tr>"""

    stats = stats_leads()

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel Conserje - Hotel Dion</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f5f5f5; }}
        h1 {{ margin-bottom: 16px; }}
        .stats {{ display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
        .stat {{ background: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .stat .n {{ font-size: 2rem; font-weight: 700; }}
        .stat .label {{ font-size: 0.85rem; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #2c3e50; color: white; padding: 10px 12px; text-align: left; font-size: 0.85rem; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 0.9rem; }}
        tr:hover {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <h1>Panel Conserje - Hotel Dion</h1>
    <div class="stats">
        <div class="stat"><div class="n">{stats['total']}</div><div class="label">Total leads</div></div>
        <div class="stat"><div class="n">{stats['por_estado'].get('nuevo', 0)}</div><div class="label">Nuevos</div></div>
        <div class="stat"><div class="n">{stats['por_estado'].get('contactado', 0)}</div><div class="label">Contactados</div></div>
        <div class="stat"><div class="n">{stats['por_estado'].get('reservado', 0)}</div><div class="label">Reservados</div></div>
    </div>
    <table>
        <thead>
            <tr><th>#</th><th>Huésped</th><th>Fechas</th><th>Personas</th><th>Habitación</th><th>Estado</th><th>Recibido</th><th>Acción</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <script>
    async function cambiarEstado(id, estado) {{
        if (!estado) return;
        await fetch('/api/leads/' + id, {{
            method: 'PATCH',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{estado: estado}})
        }});
        location.reload();
    }}
    </script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"\n  Hotel Dion - Landing page: http://localhost:{port}")
    print(f"  Panel conserje:           http://localhost:{port}/panel")
    print(f"  API leads:                http://localhost:{port}/api/leads\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
