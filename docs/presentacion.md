# Guión de Presentación — Quality Guardian
**Tiempo total: 10 minutos**

---

## Antes de empezar (preparación en VS Code)

- Abre VS Code con la carpeta del proyecto (`COIL-G8`)
- Ten estas pestañas listas en el editor (ábrelas antes):
  1. `src/engine.py`
  2. `docs/casos_prueba.md`
  3. `guardian/agent.py`
  4. `guardian/sandbox.py`
  5. `test_generated.py` (si ya existe del run anterior)
- Ten una terminal abierta en la raíz del proyecto
- Si vas a hacer live demo: asegúrate de que Ollama esté corriendo y Docker Desktop esté abierto

---

## [00:00 — 01:00] Introducción

> **Di esto:**

"Buenas. Nuestro proyecto se llama Quality Guardian. La idea es simple: tenemos un motor de despacho de inventario perecedero que aplica una regla llamada FEFO — First Expired, First Out — y queríamos que un agente de inteligencia artificial lo auditara automáticamente, sin intervención humana."

"El stack es 100% open source y corre en local: Python, LangChain, Llama 3 corriendo en Ollama, y Docker. Sin APIs de pago."

> **Acción:** Muestra el árbol de carpetas en el explorador de VS Code (panel izquierdo).

---

## [01:00 — 03:00] El motor — `src/engine.py`

> **Acción:** Abre `src/engine.py`. Señala la función `gestionar_despacho` en la línea 85.

> **Di esto:**

"Este es el núcleo del sistema. La función `gestionar_despacho` recibe un inventario, una cantidad pedida y una fecha. Hace tres cosas:"

> **Acción:** Señala cada bloque con el cursor mientras lo mencionas.

"Primero — filtra los lotes que están muy cerca de vencer. Si un lote vence en 3 días o menos, queda bloqueado y no se puede despachar."

"Segundo — con los lotes que sí están aptos, verifica que haya suficiente stock. Si no alcanza, lanza un error claro: 'Stock Insuficiente'."

"Tercero — ordena los lotes aptos por fecha de vencimiento, el más próximo primero, y va descontando unidades hasta completar el pedido. Eso es FEFO."

"Este código ya está terminado. El rol de nuestro agente no es escribirlo, es auditarlo."

---

## [03:00 — 04:30] El oráculo — `docs/casos_prueba.md`

> **Acción:** Abre `docs/casos_prueba.md`. Desplázate para que se vean los CASO 03 y CASO 04.

> **Di esto:**

"Para que el agente sepa qué probar, necesita un oráculo — una referencia de cómo se debe comportar el motor. Ese oráculo es este archivo."

"Tiene 12 escenarios. Cada uno tiene el inventario exacto en formato Python, el pedido, la fecha del sistema, y los criterios de aceptación con las assertions exactas."

> **Acción:** Señala el CASO 03 (fragmentación).

"Por ejemplo, este caso trampa: el pedido es de 10 unidades pero el lote más próximo a vencer solo tiene 5. El agente tiene que generar un test que verifique que el motor combina lotes correctamente."

> **Acción:** Señala el CASO 04 (bloqueo exacto en 3 días).

"Y este es el caso límite más delicado: un lote que vence exactamente en 3 días. ¿Se bloquea o no? Sí, se bloquea. El archivo lo documenta sin ambigüedad."

---

## [04:30 — 06:30] El agente — `guardian/agent.py`

> **Acción:** Abre `guardian/agent.py`. Desplázate hasta el bloque `_PROMPT_TEMPLATE`.

> **Di esto:**

"Aquí está el agente. Usa LangChain con una cadena simple: un `PromptTemplate`, el modelo `Llama 3 8B` corriendo en Ollama, y un parser de texto."

"Lo que hace es leer el motor y el oráculo, y le pide al modelo que genere pruebas pytest."

> **Acción:** Señala el bloque de la estructura del dict en el prompt (la sección que dice `ESTRUCTURA OBLIGATORIA`).

"Un detalle importante: el prompt le da al LLM la estructura exacta del diccionario de inventario, ejemplos de funciones de prueba y los strings exactos para los `pytest.raises`. Esto es crítico — un modelo pequeño como Llama 3 8B necesita contexto muy preciso para no inventarse cosas."

> **Acción:** Baja hasta la función `generate_tests` y señala el bloque `compile()`.

"Y antes de escribir el archivo, validamos que el código generado compile correctamente. Si el LLM devuelve código con error de sintaxis, el agente lo detecta y lanza un aviso en lugar de escribir un archivo roto."

---

## [06:30 — 07:30] El sandbox — `guardian/sandbox.py`

> **Acción:** Abre `guardian/sandbox.py`. Señala la función `run_sandbox`.

> **Di esto:**

"Una vez que tenemos los tests generados, el sandbox los ejecuta. Levanta el contenedor Docker `guardian-sandbox` con `--rm`, monta el directorio del proyecto adentro, corre pytest con reporte JSON, y lee el resultado."

> **Acción:** Señala la función `_parse_report`.

"El veredicto final es simple: si pytest no reporta fallos, el veredicto es APROBADO. Si reporta uno o más, es RECHAZADO con el conteo exacto de bugs detectados."

---

## [07:30 — 09:30] Demo / Resultado

### Opción A — Live demo (si Ollama y Docker están corriendo)

> **Acción:** En la terminal ejecuta:
```
python guardian.py
```
> Deja que corra. Comenta mientras espera:

"Estamos en la Fase 1 — el modelo está leyendo el motor y los casos de prueba y generando los tests. Dependiendo del hardware puede tomar entre 30 segundos y 3 minutos."

> Cuando termine la Fase 2, señala el veredicto en la terminal.

---

### Opción B — Mostrar resultado previo (más seguro para presentación)

> **Acción:** Abre `test_generated.py`.

> **Di esto:**

"Esto es lo que generó el agente en nuestra última ejecución. Son funciones pytest que toman los datos directamente de los casos de prueba — inventarios con IDs, fechas, cantidades — y verifican el comportamiento real del motor."

> **Acción:** Señala una función de prueba de bloqueo y una de stock insuficiente.

"Cuando estos tests corren en Docker y uno falla, no significa que el agente falló. Significa que el agente encontró algo. El éxito se mide por la precisión del reporte, no por tener cero fallos."

---

## [09:30 — 10:00] Cierre

> **Di esto:**

"En resumen: el motor de despacho implementa FEFO con bloqueo de seguridad. El agente lo audita usando un LLM local sin costo, genera pruebas específicas basadas en un oráculo documentado, y emite un veredicto reproducible en un entorno aislado."

"Todo corre en la máquina del estudiante. Sin servicios externos. Sin costo."

"Eso es todo, gracias."

---

## Posibles preguntas y respuestas rápidas

**¿Por qué Llama 3 y no ChatGPT?**
> "La HU exige stack 100% open source y sin APIs de pago. Llama 3 corre local con Ollama, cero costo, cero dependencia externa."

**¿Qué pasa si el LLM genera tests incorrectos?**
> "El agente tiene dos capas de defensa: valida sintaxis Python antes de guardar el archivo, y el oráculo en casos_prueba.md tiene los assertions exactos para guiar al modelo."

**¿El veredicto RECHAZADO significa que el motor tiene bugs?**
> "No necesariamente. Puede ser Escenario A — el agente descubrió un fallo real — o Escenario B — el LLM malinterpretó algo. La gracia del sistema es que el reporte JSON siempre dice exactamente qué test falló y por qué, para que el equipo pueda distinguir entre los dos casos."

**¿Por qué Docker para los tests?**
> "Aislamiento. Los tests no dependen del entorno del desarrollador. Si pasan en el contenedor, pasan en cualquier máquina con Docker."
