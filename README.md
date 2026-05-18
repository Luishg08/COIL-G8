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