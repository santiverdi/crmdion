"""Tests para generación de links wa.me."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.whatsapp import generar_link_wame, personalizar_mensaje_post_estadia


def test_link_wame_basico():
    link = generar_link_wame("5491112345678", "Hola test")
    assert link.startswith("https://wa.me/5491112345678?text=")
    assert "Hola%20test" in link


def test_link_wame_sin_telefono():
    assert generar_link_wame("", "Hola") == ""


def test_personalizar_mensaje():
    msg = personalizar_mensaje_post_estadia(
        nombre="PEREZ, JUAN CARLOS",
        fecha_vencimiento="15/06/2026",
    )
    assert "Hola Perez!" in msg
    assert "VUELVO10" in msg
    assert "15/06/2026" in msg
    assert "Hotel Dion" in msg


def test_personalizar_nombre_formato_apellido_nombre():
    msg = personalizar_mensaje_post_estadia(nombre=" Lopez , Nestor")
    assert "Hola Lopez!" in msg


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
