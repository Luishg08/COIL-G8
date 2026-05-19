# COIL-G8
# Quality Guardian - Logística Pro

**Agente Guardian para Controlador de Stock Perecederos (FEFO)**  
**Universidad Manuela Beltrán** - Estudiante UMB

---

## 🎯 Descripción

Agente autónomo desarrollado con **LangChain + Llama 3 8B (Ollama)** que analiza un controlador de despacho (`engine.py`), genera pruebas pytest inteligentes y las ejecuta en un contenedor **Docker aislado** para emitir un veredicto auditable.

Cumple con los requerimientos de la HU del taller **Quality Guardian · Inventario Inteligente**.

---

## ✨ Características

- 100% **open source** y local (sin APIs de pago)
- Lee automáticamente `engine.py` y `casos_prueba.md`
- Genera pruebas pytest cubriendo:
  - Regla **FEFO** (First Expired, First Out)
  - Bloqueo de seguridad (vencimiento ≤ 3 días)
  - Validación de stock insuficiente
- Ejecuta las pruebas en contenedor Docker aislado
- Emite veredicto claro: **APROBADO** o **RECHAZADO**

---

## 🚀 Cómo usarlo

### Comando principal (un solo punto de entrada)

```bash
python guardian.py

```

## Estructura del proyecto

```
quality-guardian/
├── src/
│   └── engine.py              # Motor de despacho FEFO
├── docs/
│   └── casos_prueba.md        # Matriz de trazabilidad (10 casos de prueba)
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar el motor manualmente

```bash
python src/engine.py
```

Esto ejecuta tres ejemplos de demostración: un despacho exitoso, un caso de stock insuficiente y un caso con lote bloqueado.

## Ejecutar los tests

```bash
pytest --json-report --json-report-file=report.json
```

El reporte JSON se genera en `report.json` para consumo del sandbox Docker.

## Notas

- El **Dockerfile** es responsabilidad del rol UMB (Container Builder).
- El **agente LangChain** (orquestador de pruebas con Llama 3) es responsabilidad del rol AI Engineer.
- Este entregable contiene únicamente el motor de despacho (`src/engine.py`) y la matriz de casos de prueba (`docs/casos_prueba.md`).

