"""
Quality Guardian — Punto de entrada principal.

Flujo:
  1. El agente lee engine.py y casos_prueba.md y genera test_generated.py.
  2. El sandbox ejecuta las pruebas en Docker y emite el veredicto final.
"""

import sys
from guardian.agent import generate_tests
from guardian.sandbox import run_sandbox


def main() -> int:
    print("=== Quality Guardian — Inventario Inteligente ===\n")

    print("--- Fase 1: Generación de pruebas ---")
    try:
        test_file = generate_tests()
        print(f"  Pruebas generadas: {test_file}\n")
    except Exception as exc:
        print(f"  ERROR en agente: {exc}", file=sys.stderr)
        return 1

    print("--- Fase 2: Ejecución en sandbox Docker ---")
    try:
        resultado = run_sandbox()
    except Exception as exc:
        print(f"  ERROR en sandbox: {exc}", file=sys.stderr)
        return 1

    return 0 if resultado["veredicto"] == "APROBADO" else 1


if __name__ == "__main__":
    sys.exit(main())
