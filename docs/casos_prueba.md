# Matriz de Trazabilidad — Casos de Prueba

## CT-01 — Despacho exitoso con un solo lote
- **Tipo:** Happy Path
- **Regla que valida:** R4
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "A-100", "cantidad": 100, "vencimiento": "2026-07-01"}]`
  - pedido_cliente: `50`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** Retorna una lista con un solo elemento. El lote A-100 tiene 100 unidades disponibles y no está bloqueado (vencimiento a 43 días). Se despachan 50 unidades.
- **Criterio de aceptación:**
  - `len(resultado) == 1`
  - `resultado[0]["id"] == 1`
  - `resultado[0]["lote"] == "A-100"`
  - `resultado[0]["cantidad_despachada"] == 50`
  - `resultado[0]["saldo_restante"] == 50`

---

## CT-02 — Despacho FEFO con dos lotes aptos
- **Tipo:** Happy Path
- **Regla que valida:** R1
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "A-100", "cantidad": 30, "vencimiento": "2026-06-15"}, {"id": 2, "lote": "B-200", "cantidad": 50, "vencimiento": "2026-06-01"}]`
  - pedido_cliente: `20`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** El lote B-200 vence el 2026-06-01 (13 días) y el A-100 vence el 2026-06-15 (27 días). Ambos están aptos. FEFO prioriza B-200 por ser el más próximo a vencer. Se despachan 20 unidades de B-200.
- **Criterio de aceptación:**
  - `len(resultado) == 1`
  - `resultado[0]["id"] == 2`
  - `resultado[0]["lote"] == "B-200"`
  - `resultado[0]["cantidad_despachada"] == 20`
  - `resultado[0]["saldo_restante"] == 30`

---

## CT-03 — Lote bloqueado exactamente en 3 días
- **Tipo:** Caso Borde
- **Regla que valida:** R2
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "X-100", "cantidad": 100, "vencimiento": "2026-05-22"}, {"id": 2, "lote": "Y-200", "cantidad": 100, "vencimiento": "2026-08-01"}]`
  - pedido_cliente: `50`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** El lote X-100 vence el 2026-05-22, que es exactamente 3 días después de 2026-05-19. Está BLOQUEADO. Solo Y-200 es apto. Se despachan 50 unidades de Y-200.
- **Criterio de aceptación:**
  - `len(resultado) == 1`
  - `resultado[0]["id"] == 2`
  - `resultado[0]["lote"] == "Y-200"`
  - `resultado[0]["cantidad_despachada"] == 50`
  - `resultado[0]["saldo_restante"] == 50`

---

## CT-04 — Lote bloqueado con 2 días de margen
- **Tipo:** Caso Borde
- **Regla que valida:** R2
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "Z-100", "cantidad": 200, "vencimiento": "2026-05-21"}, {"id": 2, "lote": "W-200", "cantidad": 100, "vencimiento": "2026-09-01"}]`
  - pedido_cliente: `80`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** El lote Z-100 vence el 2026-05-21, que es 2 días después de 2026-05-19. Está BLOQUEADO. Solo W-200 es apto. Se despachan 80 unidades de W-200.
- **Criterio de aceptación:**
  - `len(resultado) == 1`
  - `resultado[0]["id"] == 2`
  - `resultado[0]["lote"] == "W-200"`
  - `resultado[0]["cantidad_despachada"] == 80`
  - `resultado[0]["saldo_restante"] == 20`

---

## CT-05 — Lote con 4 días de margen (SÍ se despacha)
- **Tipo:** Caso Borde
- **Regla que valida:** R2
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "P-100", "cantidad": 60, "vencimiento": "2026-05-23"}, {"id": 2, "lote": "Q-200", "cantidad": 100, "vencimiento": "2026-10-01"}]`
  - pedido_cliente: `40`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** El lote P-100 vence el 2026-05-23, que es 4 días después de 2026-05-19. NO está bloqueado (4 > 3). Es el más próximo a vencer, así que FEFO lo selecciona primero. Se despachan 40 unidades de P-100.
- **Criterio de aceptación:**
  - `len(resultado) == 1`
  - `resultado[0]["id"] == 1`
  - `resultado[0]["lote"] == "P-100"`
  - `resultado[0]["cantidad_despachada"] == 40`
  - `resultado[0]["saldo_restante"] == 20`

---

## CT-06 — Stock insuficiente
- **Tipo:** Caso Error
- **Regla que valida:** R3
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "R-100", "cantidad": 10, "vencimiento": "2026-08-01"}, {"id": 2, "lote": "S-200", "cantidad": 15, "vencimiento": "2026-09-01"}]`
  - pedido_cliente: `50`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** Ambos lotes están aptos pero la suma de cantidades es 25 (10 + 15), que es menor que el pedido de 50. Se lanza `ValueError`.
- **Criterio de aceptación:**
  - `pytest.raises(ValueError)` con mensaje exacto `"Stock Insuficiente"`

---

## CT-07 — Inventario mixto: un lote apto y uno bloqueado
- **Tipo:** Happy Path
- **Regla que valida:** R2 + R4
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "M-100", "cantidad": 200, "vencimiento": "2026-05-20"}, {"id": 2, "lote": "N-200", "cantidad": 150, "vencimiento": "2026-07-15"}]`
  - pedido_cliente: `100`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** El lote M-100 vence el 2026-05-20, que es 1 día después de 2026-05-19. Está BLOQUEADO. Solo N-200 es apto. Se despachan 100 unidades de N-200.
- **Criterio de aceptación:**
  - `len(resultado) == 1`
  - `resultado[0]["id"] == 2`
  - `resultado[0]["lote"] == "N-200"`
  - `resultado[0]["cantidad_despachada"] == 100`
  - `resultado[0]["saldo_restante"] == 50`

---

## CT-08 — Pedido consume exactamente dos lotes completos (FEFO multilote)
- **Tipo:** Happy Path
- **Regla que valida:** R1 + R4
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "F-100", "cantidad": 30, "vencimiento": "2026-06-01"}, {"id": 2, "lote": "G-200", "cantidad": 20, "vencimiento": "2026-06-15"}, {"id": 3, "lote": "H-300", "cantidad": 100, "vencimiento": "2026-09-01"}]`
  - pedido_cliente: `50`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** Todos los lotes están aptos. FEFO ordena: F-100 (vence 2026-06-01), G-200 (vence 2026-06-15), H-300 (vence 2026-09-01). Se consumen 30 de F-100 (completo) y 20 de G-200 (completo). Total = 50.
- **Criterio de aceptación:**
  - `len(resultado) == 2`
  - `resultado[0]["id"] == 1`, `resultado[0]["cantidad_despachada"] == 30`, `resultado[0]["saldo_restante"] == 0`
  - `resultado[1]["id"] == 2`, `resultado[1]["cantidad_despachada"] == 20`, `resultado[1]["saldo_restante"] == 0`

---

## CT-09 — fecha_sistema con formato inválido
- **Tipo:** Caso Error
- **Regla que valida:** R0
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "T-100", "cantidad": 50, "vencimiento": "2026-08-01"}]`
  - pedido_cliente: `10`
  - fecha_sistema: `"19/05/2026"`
- **Resultado esperado:** El formato `"19/05/2026"` no cumple con `"YYYY-MM-DD"`. Se lanza `ValueError`.
- **Criterio de aceptación:**
  - `pytest.raises(ValueError)` con mensaje que contiene `"fecha_sistema inválida: 19/05/2026"`

---

## CT-10 — Pedido consume parcialmente el primer lote y totalmente el segundo en orden FEFO
- **Tipo:** Happy Path
- **Regla que valida:** R1 + R4
- **Entrada:**
  - inventario: `[{"id": 1, "lote": "J-100", "cantidad": 40, "vencimiento": "2026-06-10"}, {"id": 2, "lote": "K-200", "cantidad": 25, "vencimiento": "2026-06-20"}, {"id": 3, "lote": "L-300", "cantidad": 80, "vencimiento": "2026-08-01"}]`
  - pedido_cliente: `55`
  - fecha_sistema: `"2026-05-19"`
- **Resultado esperado:** Todos los lotes están aptos. FEFO ordena: J-100 (vence 2026-06-10), K-200 (vence 2026-06-20), L-300 (vence 2026-08-01). Se consumen 40 de J-100 (parcial del total necesario) y 15 de K-200 (parcial de sus 25). Total = 55. J-100 queda en 0, K-200 queda en 10. Solo se retornan J-100 y K-200 porque L-300 no fue tocado.
- **Criterio de aceptación:**
  - `len(resultado) == 2`
  - `resultado[0]["id"] == 1`, `resultado[0]["lote"] == "J-100"`, `resultado[0]["cantidad_despachada"] == 40`, `resultado[0]["saldo_restante"] == 0`
  - `resultado[1]["id"] == 2`, `resultado[1]["lote"] == "K-200"`, `resultado[1]["cantidad_despachada"] == 15`, `resultado[1]["saldo_restante"] == 10`
