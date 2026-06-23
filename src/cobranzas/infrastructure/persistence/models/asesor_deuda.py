from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from cobranzas.infrastructure.persistence.models.asesor import Asesor
    from cobranzas.infrastructure.persistence.models.deuda import Deuda


class AsesorDeuda(Base):
    __tablename__ = "asesores_deuda"

    id_asesor_deuda: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_catalogo: Mapped[int] = mapped_column(Integer, nullable=False)
    id_asesor: Mapped[Optional[int]] = mapped_column(
        ForeignKey("asesores.id_asesor"), nullable=True
    )
    id_deuda: Mapped[int] = mapped_column(
        ForeignKey("deuda.id_deuda"), nullable=False
    )
    estado: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    monto: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    monto_inicial: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    monto_mora: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    id_credito_recblue: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    fecha_asignacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_modificacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    asesor: Mapped[Optional["Asesor"]] = relationship(back_populates="asignaciones")
    deuda: Mapped["Deuda"] = relationship(back_populates="asignaciones")
