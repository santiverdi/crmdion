"""Tests para la base de datos de leads."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Usar DB temporal para tests
import database.db as db_module
db_module.DB_PATH = Path(__file__).parent / "_test_leads.db"


from database.db import actualizar_estado, guardar_lead, listar_leads, stats_leads


def setup_function():
    """Limpiar DB antes de cada test."""
    if db_module.DB_PATH.exists():
        os.remove(db_module.DB_PATH)


def teardown_function():
    """Limpiar DB después de cada test."""
    if db_module.DB_PATH.exists():
        os.remove(db_module.DB_PATH)


def test_guardar_lead():
    lead_id = guardar_lead({
        'nombre': 'Juan Pérez',
        'telefono': '1112345678',
        'email': 'juan@test.com',
        'checkin': '2026-04-01',
        'checkout': '2026-04-05',
        'adultos': 2,
        'menores': 1,
        'tipo_habitacion': 'doble',
    })
    assert lead_id == 1


def test_listar_leads():
    guardar_lead({
        'nombre': 'Test 1',
        'telefono': '111',
        'checkin': '2026-04-01',
        'checkout': '2026-04-02',
        'tipo_habitacion': 'simple',
    })
    guardar_lead({
        'nombre': 'Test 2',
        'telefono': '222',
        'checkin': '2026-04-01',
        'checkout': '2026-04-02',
        'tipo_habitacion': 'doble',
    })
    leads = listar_leads()
    assert len(leads) == 2


def test_actualizar_estado():
    lead_id = guardar_lead({
        'nombre': 'Test',
        'telefono': '111',
        'checkin': '2026-04-01',
        'checkout': '2026-04-02',
        'tipo_habitacion': 'simple',
    })
    actualizar_estado(lead_id, 'contactado')
    leads = listar_leads(estado='contactado')
    assert len(leads) == 1
    assert leads[0]['contactado_at'] is not None


def test_stats():
    guardar_lead({
        'nombre': 'A', 'telefono': '1',
        'checkin': '2026-04-01', 'checkout': '2026-04-02',
        'tipo_habitacion': 'simple',
    })
    guardar_lead({
        'nombre': 'B', 'telefono': '2',
        'checkin': '2026-04-01', 'checkout': '2026-04-02',
        'tipo_habitacion': 'doble',
    })
    actualizar_estado(1, 'reservado')

    s = stats_leads()
    assert s['total'] == 2
    assert s['por_estado']['nuevo'] == 1
    assert s['por_estado']['reservado'] == 1


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
