from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from cobranzas.infrastructure.persistence.models.asesor_deuda import AsesorDeuda
    from cobranzas.infrastructure.persistence.models.deudor import Deudor


class Deuda(Base):
    __tablename__ = "deuda"

    id_deuda: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_deudor: Mapped[int] = mapped_column(
        ForeignKey("deudores.id_deudor"), nullable=False
    )
    numero_operacion: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True
    )
    oficina: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    descripcion_oficina: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    tipo_operacion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tipo_destino: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    fecha_concesion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_ultimo_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valor_original_prestamo: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    saldo_capital_prestamo: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    calificacion: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    total_provision: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    saldo: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    fecha_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    creado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    deudor: Mapped["Deudor"] = relationship(back_populates="deudas")
    asignaciones: Mapped[List["AsesorDeuda"]] = relationship(back_populates="deuda")
