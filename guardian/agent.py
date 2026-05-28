"""
Quality Guardian — Agente LangChain para generación automática de pruebas Pytest.

Lee src/engine.py y docs/casos_prueba.md, invoca Llama 3 8B vía Ollama y
produce test_generated.py con casos que cubren FEFO, bloqueo de seguridad
y stock insuficiente.
"""

import re
import sys
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

PROJECT_ROOT = Path(__file__).parent.parent
ENGINE_PATH = PROJECT_ROOT / "src" / "engine.py"
CASOS_PATH = PROJECT_ROOT / "docs" / "casos_prueba.md"
OUTPUT_PATH = PROJECT_ROOT / "test_generated.py"

_PROMPT_TEMPLATE = """\
Eres un experto en Python y pruebas unitarias con pytest.
Tu única tarea es generar el contenido de test_generated.py a partir del \
código fuente y los casos de prueba que se muestran al final.

════════════════════════════════════════════
BLOQUE DE CABECERA — cópialo EXACTAMENTE al inicio del archivo generado:
════════════════════════════════════════════

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from engine import gestionar_despacho

════════════════════════════════════════════
ESTRUCTURA OBLIGATORIA DE CADA ELEMENTO DE INVENTARIO
════════════════════════════════════════════

Cada lote del inventario es un dict Python con EXACTAMENTE estas cuatro claves:
  "id"         → entero (1, 2, 3 …) NUNCA cadena
  "lote"       → cadena (ej. "L-001")
  "cantidad"   → entero (unidades disponibles)
  "vencimiento"→ cadena con formato "YYYY-MM-DD"

Ejemplo correcto:
  inventario = [
      {{"id": 1, "lote": "L-001", "cantidad": 50, "vencimiento": "2026-06-30"}},
      {{"id": 2, "lote": "L-002", "cantidad": 20, "vencimiento": "2026-07-15"}},
  ]

════════════════════════════════════════════
PATRONES DE PRUEBA — úsalos como plantilla exacta
════════════════════════════════════════════

# Patrón A — despacho exitoso:
def test_nombre_descriptivo():
    inventario = [
        {{"id": 1, "lote": "L-XXX", "cantidad": 30, "vencimiento": "2026-06-10"}},
        {{"id": 2, "lote": "L-YYY", "cantidad": 30, "vencimiento": "2026-07-15"}},
    ]
    resultado = gestionar_despacho(inventario, 25, "2026-05-27")
    assert len(resultado) == 1
    assert resultado[0]["lote"] == "L-XXX"
    assert resultado[0]["cantidad_despachada"] == 25
    assert resultado[0]["saldo_restante"] == 5

# Patrón B — error de stock insuficiente (usa este match EXACTO, respeta mayúsculas):
def test_stock_insuficiente():
    inventario = [
        {{"id": 1, "lote": "L-ZZZ", "cantidad": 3, "vencimiento": "2026-09-01"}},
    ]
    with pytest.raises(ValueError, match="Stock Insuficiente"):
        gestionar_despacho(inventario, 10, "2026-05-27")

# Patrón C — lote bloqueado (vence en ≤ 3 días se excluye; el apto sí se usa):
def test_bloqueo_seguridad():
    inventario = [
        {{"id": 1, "lote": "L-BLQ", "cantidad": 40, "vencimiento": "2026-05-30"}},  # bloqueado: 3 días
        {{"id": 2, "lote": "L-APT", "cantidad": 30, "vencimiento": "2026-08-01"}},  # apto
    ]
    resultado = gestionar_despacho(inventario, 15, "2026-05-27")
    assert len(resultado) == 1
    assert resultado[0]["lote"] == "L-APT"

════════════════════════════════════════════
STRINGS DE match= PARA pytest.raises — úsalos literalmente
════════════════════════════════════════════

  Stock insuficiente : match="Stock Insuficiente"
  Fecha inválida     : match="fecha_sistema inválida"

════════════════════════════════════════════
ESCENARIOS QUE DEBES CUBRIR (mínimo 5 funciones de prueba)
════════════════════════════════════════════

1. FEFO básico — con dos lotes aptos, se despacha primero el que vence antes.
2. Fragmentación — el pedido supera la cantidad del primer lote; el motor combina lotes.
3. Bloqueo exacto en 3 días — el lote queda excluido; solo el apto recibe despacho.
4. Stock insuficiente — suma de aptos < pedido → ValueError("Stock Insuficiente").
5. Combinación FEFO + bloqueo — hay lotes bloqueados y aptos; FEFO aplica solo sobre los aptos.

════════════════════════════════════════════
REGLAS FINALES
════════════════════════════════════════════

- Genera SOLO código Python puro, sin markdown, sin explicaciones, sin bloques ```.
- Todos los "id" deben ser enteros (1, 2, 3), nunca cadenas como "L-001".
- Usa los casos del archivo casos_prueba.md como fuente de datos para los tests.
- No inventes comportamientos que no estén en engine.py.

## Código fuente — src/engine.py:
{engine_code}

## Casos de prueba documentados — docs/casos_prueba.md:
{casos_text}

Genera ÚNICAMENTE el código Python del archivo test_generated.py:\
"""


def _extract_python(text: str) -> str:
    """Extrae código Python limpio de la respuesta del LLM."""
    match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def generate_tests(model: str = "llama3") -> Path:
    """Genera test_generated.py usando Llama 3 8B vía Ollama.

    Args:
        model: nombre del modelo Ollama a usar (por defecto llama3).

    Returns:
        Ruta absoluta del archivo test_generated.py producido.
    """
    engine_code = ENGINE_PATH.read_text(encoding="utf-8")
    casos_text = CASOS_PATH.read_text(encoding="utf-8")

    llm = OllamaLLM(model=model, temperature=0)
    prompt = PromptTemplate.from_template(_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    print(f"[agent] Invocando {model} para generar pruebas…")
    raw_output = chain.invoke({"engine_code": engine_code, "casos_text": casos_text})

    python_code = _extract_python(raw_output)

    try:
        compile(python_code, "<test_generated>", "exec")
    except SyntaxError as exc:
        raise RuntimeError(
            f"El LLM generó código con error de sintaxis: {exc}\n"
            f"Fragmento recibido:\n{python_code[:400]}"
        ) from exc

    OUTPUT_PATH.write_text(python_code, encoding="utf-8")
    print(f"[agent] Pruebas escritas en: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    model_arg = sys.argv[1] if len(sys.argv) > 1 else "llama3"
    generate_tests(model=model_arg)
