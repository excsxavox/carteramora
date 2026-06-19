from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String
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
        String(50), nullable=True, index=True
    )
    fecha_corte: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, index=True
    )
    archivo_origen: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fecha_carga: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    oficina: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    desc_oficina: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    socio: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nombre: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    cedula: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo_operacion: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo_destino: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fecha_concesion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_ultimo_pago: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valor_original_prestamo: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    saldo_capital_prestamo: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    calificacion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_provision: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    saldo_140x: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    saldo_141x: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    saldo_142x: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    interes_normal: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    interes_devengado: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    interes_vencido: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    interes_resolucion: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    interes_castigado: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    interes_mora: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    otros_rubros_deuda: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    total_operacion: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(38, 10), nullable=True
    )
    estado: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    oficial: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    dias_mora: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dias_atraso_camorosico: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    fecha_ingreso: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dia_pago: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    valor_cuota: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    cuota_actual: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dividendos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cod_oficial_asignado: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    oficial_asignado: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    cod_oficial_adm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    oficial_adm: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    operacion_homologada: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    decision: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    segmentacion: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    score: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fuente_repago: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    identificacion_ifi: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    actividad_economica: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    fecha_archivo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tipo_mes: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    tipo_fideicomiso: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    proceso_cod: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    creado_en: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    deudor: Mapped["Deudor"] = relationship(back_populates="deudas")
    asignaciones: Mapped[List["AsesorDeuda"]] = relationship(back_populates="deuda")
