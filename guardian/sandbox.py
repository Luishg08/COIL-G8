"""
Quality Guardian — Sandbox Docker para ejecución aislada de pruebas pytest.

Lanza el contenedor guardian-sandbox con --rm, monta el directorio del proyecto
y ejecuta pytest --json-report. Lee .report.json y emite un veredicto auditable.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_FILE = PROJECT_ROOT / ".report.json"
IMAGE_NAME = "guardian-sandbox"
DOCKERFILE = PROJECT_ROOT / "Dockerfile"


def _image_exists() -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", IMAGE_NAME],
        capture_output=True,
    )
    return result.returncode == 0


def _build_image() -> None:
    print(f"[sandbox] Construyendo imagen {IMAGE_NAME}…")
    subprocess.run(
        ["docker", "build", "-t", IMAGE_NAME, str(PROJECT_ROOT)],
        check=True,
    )
    print(f"[sandbox] Imagen {IMAGE_NAME} lista.")


def _run_container() -> int:
    """Ejecuta los tests en el contenedor y retorna el código de salida."""
    # Docker Desktop en Windows acepta rutas Windows directamente.
    mount = f"{PROJECT_ROOT}:/app"
    cmd = [
        "docker", "run", "--rm",
        "-v", mount,
        IMAGE_NAME,
        "pytest", "--json-report",
        "--tb=short", "-q",
    ]
    print(f"[sandbox] Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def _parse_report() -> dict:
    """Lee .report.json y construye el resumen con veredicto."""
    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el reporte en {REPORT_FILE}. "
            "Verifica que pytest-json-report esté instalado en el contenedor."
        )

    report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    summary = report.get("summary", {})

    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    bugs_detectados = failed
    veredicto = "APROBADO" if failed == 0 else "RECHAZADO"

    return {
        "passed": passed,
        "failed": failed,
        "bugs_detectados": bugs_detectados,
        "veredicto": veredicto,
    }


def run_sandbox() -> dict:
    """Lanza el sandbox Docker, ejecuta pytest y retorna el veredicto.

    Returns:
        Diccionario con las claves:
            - passed (int): número de pruebas exitosas.
            - failed (int): número de pruebas fallidas.
            - bugs_detectados (int): igual a failed.
            - veredicto (str): "APROBADO" si failed == 0, "RECHAZADO" si no.

    Raises:
        FileNotFoundError: si .report.json no se genera tras la ejecución.
        subprocess.CalledProcessError: si falla la construcción de la imagen.
    """
    if not _image_exists():
        _build_image()

    _run_container()
    resultado = _parse_report()

    print(f"\n[sandbox] === VEREDICTO ===")
    print(f"  Pasadas : {resultado['passed']}")
    print(f"  Fallidas: {resultado['failed']}")
    print(f"  Bugs    : {resultado['bugs_detectados']}")
    print(f"  Resultado: {resultado['veredicto']}")
    return resultado


if __name__ == "__main__":
    try:
        run_sandbox()
    except Exception as exc:
        print(f"[sandbox] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
