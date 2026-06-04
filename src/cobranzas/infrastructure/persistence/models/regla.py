from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cobranzas.infrastructure.persistence.base import Base


class Regla(Base):
    __tablename__ = "reglas"

    id_regla: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    valor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prioridad: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)
    creado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    fecha_modificacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
