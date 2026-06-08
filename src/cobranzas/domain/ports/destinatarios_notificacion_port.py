from pathlib import Path
from typing import List, Protocol

from cobranzas.domain.models.destinatario_notificacion import DestinatarioNotificacion


class DestinatariosNotificacionPort(Protocol):
    def leer_destinatarios(self, archivo_excel: Path) -> List[DestinatarioNotificacion]:
        ...
