from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

TIPO_ARCHIVO_MOROSIDAD = "morosidad"
TIPO_ARCHIVO_MORA = "mora"
ESTADO_LOTE_CARGADO = "cargado"


class TmpLoteCarga(Base):
    """Lote de carga desde archivos .lis limpios (post-job de limpieza)."""

    __tablename__ = "tmp_lote_carga"

    id_lote: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_carga: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    ruta_archivo_morosidad: Mapped[str] = mapped_column(String(500))
    ruta_archivo_mora: Mapped[str] = mapped_column(String(500))
    estado: Mapped[str] = mapped_column(String(30), default=ESTADO_LOTE_CARGADO)
    filas_morosidad: Mapped[int] = mapped_column(Integer, default=0)
    filas_mora: Mapped[int] = mapped_column(Integer, default=0)

    columnas: Mapped[List["TmpColumnaArchivo"]] = relationship(
        back_populates="lote", cascade="all, delete-orphan"
    )
    filas_morosidad_rel: Mapped[List["TmpStgMorosidad"]] = relationship(
        back_populates="lote", cascade="all, delete-orphan"
    )
    filas_mora_rel: Mapped[List["TmpStgMora"]] = relationship(
        back_populates="lote", cascade="all, delete-orphan"
    )


class TmpColumnaArchivo(Base):
    """Catálogo de columnas por archivo y lote (base para mapeo a tablas finales)."""

    __tablename__ = "tmp_columna_archivo"

    id_columna: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_lote: Mapped[int] = mapped_column(
        ForeignKey("tmp_lote_carga.id_lote"), nullable=False
    )
    tipo_archivo: Mapped[str] = mapped_column(String(20), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_columna: Mapped[str] = mapped_column(String(120), nullable=False)
    nombre_original: Mapped[str] = mapped_column(String(250), nullable=False)

    lote: Mapped["TmpLoteCarga"] = relationship(back_populates="columnas")


class TmpStgMorosidad(Base):
    """Staging: detalle_morosidad.lis (una fila por operación)."""

    __tablename__ = "tmp_stg_morosidad"

    id_fila: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_lote: Mapped[int] = mapped_column(
        ForeignKey("tmp_lote_carga.id_lote"), nullable=False, index=True
    )
    numero_fila: Mapped[int] = mapped_column(Integer, nullable=False)
    no_operacion: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    campos_json: Mapped[str] = mapped_column(Text, nullable=False)

    lote: Mapped["TmpLoteCarga"] = relationship(back_populates="filas_morosidad_rel")


class TmpStgMora(Base):
    """Staging: reporte_mora.lis (operaciones en mora enriquecidas)."""

    __tablename__ = "tmp_stg_mora"

    id_fila: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_lote: Mapped[int] = mapped_column(
        ForeignKey("tmp_lote_carga.id_lote"), nullable=False, index=True
    )
    numero_fila: Mapped[int] = mapped_column(Integer, nullable=False)
    no_operacion: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    campos_json: Mapped[str] = mapped_column(Text, nullable=False)

    lote: Mapped["TmpLoteCarga"] = relationship(back_populates="filas_mora_rel")


class TmpMapeoColumna(Base):
    """Reglas de mapeo columna staging → tabla destino (se completan en pasos siguientes)."""

    __tablename__ = "tmp_mapeo_columna"

    id_mapeo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_archivo: Mapped[str] = mapped_column(String(20), nullable=False)
    columna_origen: Mapped[str] = mapped_column(String(120), nullable=False)
    tabla_destino: Mapped[str] = mapped_column(String(80), nullable=False)
    columna_destino: Mapped[str] = mapped_column(String(120), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
