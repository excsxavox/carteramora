from typing import Protocol, Sequence


class CorreoPort(Protocol):
    def enviar(
        self,
        destinatarios: Sequence[str],
        asunto: str,
        cuerpo: str,
    ) -> None:
        ...
