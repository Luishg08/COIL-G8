"""
Quality Guardian — Motor de despacho FEFO (First Expired, First Out).

Este módulo proporciona la función `gestionar_despacho` que selecciona lotes
de inventario para cumplir un pedido de cliente siguiendo la política FEFO,
respetando bloqueos de seguridad por proximidad de vencimiento.
"""

from datetime import date


# --- Validación y parsing de fechas ---

def _parsear_fecha(cadena_fecha: str) -> date:
    """Convierte una cadena 'YYYY-MM-DD' en un objeto datetime.date.

    Args:
        cadena_fecha: fecha en formato de cadena 'YYYY-MM-DD'.

    Returns:
        Objeto date correspondiente.

    Raises:
        ValueError: si el formato es incorrecto o la fecha no es válida.
    """
    partes = cadena_fecha.split("-")
    if len(partes) != 3:
        raise ValueError(f"fecha_sistema inválida: {cadena_fecha}")

    anio_str, mes_str, dia_str = partes

    if len(anio_str) != 4 or len(mes_str) != 2 or len(dia_str) != 2:
        raise ValueError(f"fecha_sistema inválida: {cadena_fecha}")

    if not (anio_str.isdigit() and mes_str.isdigit() and dia_str.isdigit()):
        raise ValueError(f"fecha_sistema inválida: {cadena_fecha}")

    anio = int(anio_str)
    mes = int(mes_str)
    dia = int(dia_str)

    try:
        return date(anio, mes, dia)
    except ValueError:
        raise ValueError(f"fecha_sistema inválida: {cadena_fecha}")


# --- Reglas de negocio ---

def _lote_bloqueado(fecha_vencimiento: date, fecha_sistema: date) -> bool:
    """Determina si un lote está bloqueado por proximidad de vencimiento.

    Un lote se bloquea cuando la diferencia entre su vencimiento y la
    fecha del sistema es de 3 días o menos (incluyendo el día exacto).

    Args:
        fecha_vencimiento: fecha de vencimiento del lote.
        fecha_sistema: fecha actual del sistema.

    Returns:
        True si el lote está bloqueado, False en caso contrario.
    """
    diferencia_dias = (fecha_vencimiento - fecha_sistema).days
    return diferencia_dias <= 3


def _ordenar_lotes_fefo(lotes_aptos: list[dict]) -> list[dict]:
    """Ordena los lotes aptos según la regla FEFO.

    Criterio de ordenamiento:
      1. Fecha de vencimiento más próxima primero (ascendente).
      2. En caso de empate, menor id primero (ascendente).

    Args:
        lotes_aptos: lista de diccionarios con clave 'vencimiento' (date) e 'id' (int).

    Returns:
        Nueva lista ordenada según FEFO.
    """
    return sorted(lotes_aptos, key=lambda lote: (lote["vencimiento"], lote["id"]))


# --- Función principal ---

def gestionar_despacho(
    inventario: list[dict],
    pedido_cliente: int,
    fecha_sistema: str,
) -> list[dict]:
    """Gestiona el despacho de un pedido aplicando la política FEFO.

    Selecciona lotes del inventario para satisfacer la cantidad solicitada
    por el cliente, priorizando los lotes con fecha de vencimiento más
    próxima y excluyendo aquellos bloqueados por proximidad de vencimiento
    (3 días o menos).

    Args:
        inventario: lista de diccionarios, cada uno con las claves
            'id' (int), 'lote' (str), 'cantidad' (int), 'vencimiento' (str).
        pedido_cliente: cantidad de unidades solicitadas por el cliente.
        fecha_sistema: fecha actual del sistema en formato 'YYYY-MM-DD'.

    Returns:
        Lista de diccionarios con las claves 'id', 'lote',
        'cantidad_despachada' y 'saldo_restante', solo para los lotes
        que recibieron despacho (cantidad_despachada > 0).

    Raises:
        ValueError: si fecha_sistema tiene formato inválido o no es una
            fecha real, con mensaje 'fecha_sistema inválida: <valor>'.
        ValueError: si el stock disponible es inferior al pedido, con
            mensaje 'Stock Insuficiente'.
    """
    # --- R0: Validación de fecha del sistema ---
    fecha_referencia = _parsear_fecha(fecha_sistema)

    # --- R2: Filtrado de lotes bloqueados ---
    lotes_con_fecha = []
    for item in inventario:
        fecha_venc = _parsear_fecha(item["vencimiento"])
        lotes_con_fecha.append({
            "id": item["id"],
            "lote": item["lote"],
            "cantidad": item["cantidad"],
            "vencimiento": fecha_venc,
        })

    lotes_aptos = [
        lote for lote in lotes_con_fecha
        if not _lote_bloqueado(lote["vencimiento"], fecha_referencia)
    ]

    # --- R3: Validación de existencias ---
    stock_disponible = sum(lote["cantidad"] for lote in lotes_aptos)
    if stock_disponible < pedido_cliente:
        raise ValueError("Stock Insuficiente")

    # --- R1: Ordenamiento FEFO ---
    lotes_ordenados = _ordenar_lotes_fefo(lotes_aptos)

    # --- R4: Cálculo de salida ---
    resultado_despacho = []
    unidades_restantes = pedido_cliente

    for lote in lotes_ordenados:
        if unidades_restantes <= 0:
            break

        cantidad_a_despachar = min(lote["cantidad"], unidades_restantes)
        saldo_restante = lote["cantidad"] - cantidad_a_despachar
        unidades_restantes -= cantidad_a_despachar

        resultado_despacho.append({
            "id": lote["id"],
            "lote": lote["lote"],
            "cantidad_despachada": cantidad_a_despachar,
            "saldo_restante": saldo_restante,
        })

    return resultado_despacho


if __name__ == "__main__":
    print("=== Quality Guardian — Motor de Despacho FEFO ===\n")

    # --- Ejemplo 1: Despacho exitoso ---
    print("--- Ejemplo 1: Despacho exitoso ---")
    inventario_ejemplo = [
        {"id": 1, "lote": "A-100", "cantidad": 50, "vencimiento": "2026-06-15"},
        {"id": 2, "lote": "B-200", "cantidad": 30, "vencimiento": "2026-06-01"},
        {"id": 3, "lote": "C-300", "cantidad": 80, "vencimiento": "2026-07-20"},
    ]
    try:
        despacho = gestionar_despacho(inventario_ejemplo, 60, "2026-05-19")
        for linea in despacho:
            print(f"  Lote {linea['lote']} (ID {linea['id']}): "
                  f"despachados={linea['cantidad_despachada']}, "
                  f"saldo={linea['saldo_restante']}")
    except ValueError as error:
        print(f"  Error: {error}")

    print()

    # --- Ejemplo 2: Despacho fallido por stock insuficiente ---
    print("--- Ejemplo 2: Stock insuficiente ---")
    inventario_limitado = [
        {"id": 1, "lote": "X-100", "cantidad": 10, "vencimiento": "2026-08-01"},
    ]
    try:
        despacho = gestionar_despacho(inventario_limitado, 50, "2026-05-19")
        for linea in despacho:
            print(f"  Lote {linea['lote']} (ID {linea['id']}): "
                  f"despachados={linea['cantidad_despachada']}, "
                  f"saldo={linea['saldo_restante']}")
    except ValueError as error:
        print(f"  Error: {error}")

    print()

    # --- Ejemplo 3: Lote bloqueado por proximidad ---
    print("--- Ejemplo 3: Lote bloqueado (vence en 2 días) ---")
    inventario_bloqueado = [
        {"id": 1, "lote": "D-400", "cantidad": 100, "vencimiento": "2026-05-21"},
        {"id": 2, "lote": "E-500", "cantidad": 100, "vencimiento": "2026-06-30"},
    ]
    try:
        despacho = gestionar_despacho(inventario_bloqueado, 50, "2026-05-19")
        for linea in despacho:
            print(f"  Lote {linea['lote']} (ID {linea['id']}): "
                  f"despachados={linea['cantidad_despachada']}, "
                  f"saldo={linea['saldo_restante']}")
    except ValueError as error:
        print(f"  Error: {error}")
