# casos_prueba.md — Escenarios de Prueba para el Agente Guardian

> **Proyecto COIL · UMB × U. Caldas**  
> Autor: QA Team  
> Fecha de creación: 2026-05-27  
> Motor evaluado: `src/engine.py`  
> Formato de fechas: YYYY-MM-DD

---

## Reglas de negocio cubiertas

| Código | Regla |
|--------|-------|
| R1 | FEFO — se despacha primero el lote más próximo a vencer |
| R2 | Bloqueo de seguridad — lotes que vencen en ≤ 3 días quedan bloqueados |
| R3 | Stock insuficiente — si la suma de unidades aptas es menor al pedido, se lanza ValueError("Stock Insuficiente") |
| R4 | Filtrado por aptitud — solo se despachan lotes NO bloqueados |

---

## CASO 01 — FEFO básico: un solo lote disponible

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-001", "cantidad": 50, "vencimiento": "2026-06-30"}]` |
| **Pedido** | 20 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | Despacho de 20 unidades desde `L-001`. Sin errores. |
| **Regla validada** | R1 |

**Criterios de aceptación:**
- `len(resultado) == 1`
- `resultado[0]["lote"] == "L-001"`
- `resultado[0]["cantidad_despachada"] == 20`
- `resultado[0]["saldo_restante"] == 30`

---

## CASO 02 — FEFO con dos lotes: debe elegir el más próximo a vencer

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-002", "cantidad": 30, "vencimiento": "2026-06-10"}, {"id": 2, "lote": "L-003", "cantidad": 30, "vencimiento": "2026-07-15"}]` |
| **Pedido** | 25 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-002` vence antes (2026-06-10). FEFO lo elige primero. Se despachan 25 de `L-002`. `L-003` no se toca. |
| **Regla validada** | R1 |

**Criterios de aceptación:**
- `len(resultado) == 1`
- `resultado[0]["lote"] == "L-002"`
- `resultado[0]["cantidad_despachada"] == 25`
- `resultado[0]["saldo_restante"] == 5`

---

## CASO 03 — Fragmentación de despacho: pedido supera un solo lote (trampa FEFO)

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-004", "cantidad": 5, "vencimiento": "2026-06-05"}, {"id": 2, "lote": "L-005", "cantidad": 20, "vencimiento": "2026-07-01"}]` |
| **Pedido** | 10 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | FEFO agota primero `L-004` (5 u) y toma 5 más de `L-005`. Total: 10. Sin error. |
| **Regla validada** | R1 + R4 |

**Criterios de aceptación:**
- `len(resultado) == 2`
- `resultado[0]["lote"] == "L-004"` y `resultado[0]["cantidad_despachada"] == 5` y `resultado[0]["saldo_restante"] == 0`
- `resultado[1]["lote"] == "L-005"` y `resultado[1]["cantidad_despachada"] == 5` y `resultado[1]["saldo_restante"] == 15`

---

## CASO 04 — Bloqueo de seguridad exacto en 3 días (límite R2)

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-006", "cantidad": 40, "vencimiento": "2026-05-30"}]` |
| **Pedido** | 15 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-006` vence el 2026-05-30: diferencia = 3 días → BLOQUEADO por R2. Stock apto = 0 < 15. Lanza `ValueError("Stock Insuficiente")`. |
| **Regla validada** | R2 |

**Criterios de aceptación:**
- `pytest.raises(ValueError, match="Stock Insuficiente")`

---

## CASO 05 — Bloqueo de seguridad: lote vence en 1 día

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-007", "cantidad": 25, "vencimiento": "2026-05-28"}]` |
| **Pedido** | 10 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-007` vence en 1 día → BLOQUEADO. Stock apto = 0 < 10. Lanza `ValueError("Stock Insuficiente")`. |
| **Regla validada** | R2 |

**Criterios de aceptación:**
- `pytest.raises(ValueError, match="Stock Insuficiente")`

---

## CASO 06 — Filtrado por aptitud: lote apto + lote bloqueado en simultáneo

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-008", "cantidad": 20, "vencimiento": "2026-05-29"}, {"id": 2, "lote": "L-009", "cantidad": 30, "vencimiento": "2026-08-10"}]` |
| **Pedido** | 15 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-008` vence en 2 días → BLOQUEADO. Solo `L-009` es apto. Se despachan 15 de `L-009`. |
| **Regla validada** | R2 + R4 |

**Criterios de aceptación:**
- `len(resultado) == 1`
- `resultado[0]["lote"] == "L-009"`
- `resultado[0]["cantidad_despachada"] == 15`
- `resultado[0]["saldo_restante"] == 15`

---

## CASO 07 — Stock insuficiente: suma de aptos menor al pedido

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-010", "cantidad": 3, "vencimiento": "2026-09-01"}, {"id": 2, "lote": "L-011", "cantidad": 4, "vencimiento": "2026-09-15"}]` |
| **Pedido** | 10 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | Ambos aptos. Suma = 3 + 4 = 7 < 10. Lanza `ValueError("Stock Insuficiente")`. No hay despacho parcial. |
| **Regla validada** | R3 |

**Criterios de aceptación:**
- `pytest.raises(ValueError, match="Stock Insuficiente")`

---

## CASO 08 — Stock insuficiente con lote bloqueado que aparentemente completaría el pedido

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-012", "cantidad": 6, "vencimiento": "2026-05-28"}, {"id": 2, "lote": "L-013", "cantidad": 3, "vencimiento": "2026-10-01"}]` |
| **Pedido** | 8 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-012` BLOQUEADO (1 día). Solo `L-013` apto: 3 u < 8. Lanza `ValueError("Stock Insuficiente")`. El motor NO usa el lote bloqueado aunque la suma total daría 9. |
| **Regla validada** | R2 + R3 + R4 |

**Criterios de aceptación:**
- `pytest.raises(ValueError, match="Stock Insuficiente")`

---

## CASO 09 — Pedido exactamente igual al stock apto disponible

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-014", "cantidad": 10, "vencimiento": "2026-07-20"}]` |
| **Pedido** | 10 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | Despacho completo: 10 de `L-014`. Saldo resultante: 0. Sin error. |
| **Regla validada** | R1 + R3 |

**Criterios de aceptación:**
- `len(resultado) == 1`
- `resultado[0]["lote"] == "L-014"`
- `resultado[0]["cantidad_despachada"] == 10`
- `resultado[0]["saldo_restante"] == 0`

---

## CASO 10 — Combinación compleja: FEFO + bloqueo + fragmentación + stock justo

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-015", "cantidad": 8, "vencimiento": "2026-05-29"}, {"id": 2, "lote": "L-016", "cantidad": 5, "vencimiento": "2026-06-03"}, {"id": 3, "lote": "L-017", "cantidad": 7, "vencimiento": "2026-06-20"}]` |
| **Pedido** | 12 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-015` BLOQUEADO (2 días). FEFO sobre aptos: primero `L-016` (5 u), luego `L-017` (7 u). Total = 12. Sin error. |
| **Regla validada** | R1 + R2 + R4 |

**Criterios de aceptación:**
- `len(resultado) == 2`
- `resultado[0]["lote"] == "L-016"` y `resultado[0]["cantidad_despachada"] == 5` y `resultado[0]["saldo_restante"] == 0`
- `resultado[1]["lote"] == "L-017"` y `resultado[1]["cantidad_despachada"] == 7` y `resultado[1]["saldo_restante"] == 0`

---

## CASO 11 — QA propio: inventario vacío

| Campo | Valor |
|-------|-------|
| **Inventario** | `[]` (lista vacía, sin ningún lote) |
| **Pedido** | 5 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | Sin lotes en inventario, stock apto = 0 < 5. Lanza `ValueError("Stock Insuficiente")`. El motor no debe lanzar ninguna otra excepción. |
| **Regla validada** | R3 |

**Criterios de aceptación:**
- `pytest.raises(ValueError, match="Stock Insuficiente")`

---

## CASO 12 — QA propio: todos los lotes bloqueados, múltiples reglas combinadas (R1+R2+R3+R4)

| Campo | Valor |
|-------|-------|
| **Inventario** | `[{"id": 1, "lote": "L-018", "cantidad": 15, "vencimiento": "2026-05-28"}, {"id": 2, "lote": "L-019", "cantidad": 20, "vencimiento": "2026-05-29"}, {"id": 3, "lote": "L-020", "cantidad": 10, "vencimiento": "2026-05-30"}]` |
| **Pedido** | 10 unidades |
| **Fecha sistema** | `"2026-05-27"` |
| **Salida esperada** | `L-018` (1 día), `L-019` (2 días) y `L-020` (3 días exactos) → todos BLOQUEADOS por R2. Stock apto = 0. Lanza `ValueError("Stock Insuficiente")`. |
| **Regla validada** | R1 + R2 + R3 + R4 |

**Criterios de aceptación:**
- `pytest.raises(ValueError, match="Stock Insuficiente")`

---

*Fin del archivo — 12 escenarios documentados (mínimo requerido: 10)*
