"""Normalización de fecha de corte para rutas y API."""

from datetime import date, datetime


def normalizar_fecha_corte(texto: str) -> str:
    """
    Acepta DDMMYYYY (05062026) o ISO YYYY-MM-DD y devuelve DDMMYYYY.
    """
    valor = (texto or "").strip()
    if not valor:
        raise ValueError("La fecha es obligatoria")

    if len(valor) == 8 and valor.isdigit():
        datetime.strptime(valor, "%d%m%Y")
        return valor

    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor[:10], formato).date().strftime("%d%m%Y")
        except ValueError:
            continue

    raise ValueError(
        f"Formato de fecha no válido: {texto!r}. Use DDMMYYYY o YYYY-MM-DD."
    )


def fecha_corte_desde_texto(texto: str) -> date:
    return datetime.strptime(normalizar_fecha_corte(texto), "%d%m%Y").date()
