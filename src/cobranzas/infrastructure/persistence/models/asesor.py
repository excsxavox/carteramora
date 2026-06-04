from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from cobranzas.infrastructure.persistence.models.asesor_deuda import AsesorDeuda


class Asesor(Base):
    __tablename__ = "asesores"

    id_asesor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    cedula: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    numero_telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)
    creado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    asignaciones: Mapped[List["AsesorDeuda"]] = relationship(
        back_populates="asesor",
    )
