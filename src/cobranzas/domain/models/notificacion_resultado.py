from dataclasses import dataclass, field
from typing import List


@dataclass
class NotificacionResultado:
    enviado: bool = False
    destinatarios: List[str] = field(default_factory=list)
    omitido_motivo: str = ""
    errores: List[str] = field(default_factory=list)
