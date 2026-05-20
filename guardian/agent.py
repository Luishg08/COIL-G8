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
A continuación encontrarás el código fuente de un motor de despacho FEFO y los
casos de prueba documentados.

Tu tarea: generar un archivo Python válido con pruebas pytest que cubran
exactamente los tres escenarios siguientes:

1. **FEFO** — cuando hay varios lotes aptos, se despacha primero el que vence
   antes (fecha de vencimiento más próxima a fecha_sistema).
2. **Bloqueo de seguridad** — un lote que vence en 3 días o menos está bloqueado
   y no se despacha; uno que vence en 4 días o más sí se despacha.
3. **Stock insuficiente** — cuando la suma de unidades aptas es menor al pedido,
   se lanza ValueError con mensaje exacto "Stock Insuficiente".

Reglas para el archivo generado:
- La primera sección debe añadir src/ al sys.path usando Path(__file__).
- Importar gestionar_despacho desde engine (no desde src.engine).
- Usar pytest.raises(ValueError, match=...) para los casos de error.
- Incluir al menos una función de prueba por cada uno de los 3 escenarios.
- NO incluir markdown, bloques de código ni explicaciones: solo código Python puro.

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
    OUTPUT_PATH.write_text(python_code, encoding="utf-8")
    print(f"[agent] Pruebas escritas en: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    model_arg = sys.argv[1] if len(sys.argv) > 1 else "llama3"
    generate_tests(model=model_arg)
