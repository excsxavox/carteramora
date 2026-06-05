from dataclasses import dataclass, field

from cobranzas.infrastructure.config.settings import Settings


@dataclass
class PipelineContext:
    """Contexto compartido de la cadena pre-limpieza (Jobs 0, 0b, 1)."""

    settings: Settings
    codigo_salida: int = 0
    detener: bool = False
    mensajes: list[str] = field(default_factory=list)
