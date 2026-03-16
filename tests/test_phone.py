"""Tests para normalización de teléfonos argentinos."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.phone import extraer_movil, normalizar_argentino, telefono_para_wame


def test_extraer_movil_con_fijo():
    raw = "Mov: +54 9 11 3702-9115 - Fij: +54 9 11 3702-9115"
    assert extraer_movil(raw) == "+54 9 11 3702-9115"


def test_extraer_movil_simple():
    assert extraer_movil("Mov: +54 9 11 6263-1970") == "+54 9 11 6263-1970"


def test_extraer_movil_sin_prefijo_internacional():
    assert extraer_movil("Mov: 3413360302") == "3413360302"


def test_extraer_movil_vacio():
    assert extraer_movil("") == ""
    assert extraer_movil(None) == ""


def test_normalizar_ya_internacional():
    assert normalizar_argentino("+54 9 11 3702-9115") == "5491137029115"


def test_normalizar_10_digitos():
    assert normalizar_argentino("3413360302") == "5493413360302"


def test_normalizar_con_549():
    assert normalizar_argentino("5492216775355") == "5492216775355"


def test_normalizar_sin_9():
    # +54 11 3030 1677 → falta el 9
    assert normalizar_argentino("+54 11 3030 1677") == "5491130301677"


def test_normalizar_11_digitos_con_9():
    assert normalizar_argentino("92914126036") == "5492914126036"


def test_normalizar_vacio():
    assert normalizar_argentino("") == ""


def test_pipeline_completo():
    raw = "Mov: +54 9 11 6877-8401 - Fij: +54 9 11 6877-8401"
    assert telefono_para_wame(raw) == "5491168778401"


def test_pipeline_10_digitos():
    raw = "Mov: 2262628274 - Fij: 2262628274"
    assert telefono_para_wame(raw) == "5492262628274"


def test_pipeline_sin_formato():
    raw = "Mov: 1140852853 - Fij: 1140852853"
    result = telefono_para_wame(raw)
    assert result.startswith("549")
    assert len(result) == 13


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
