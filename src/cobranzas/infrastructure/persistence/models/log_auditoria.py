from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cobranzas.infrastructure.persistence.base import Base


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id_log: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tabla: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    operacion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    usuario: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    datos_anteriores: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    datos_nuevos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    registrado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
