from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cobranzas.infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from cobranzas.infrastructure.persistence.models.clave import Clave


class Catalogo(Base):
    __tablename__ = "catalogo"

    id_catalogo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_clave: Mapped[int] = mapped_column(
        ForeignKey("claves.id_clave"), nullable=False
    )
    valor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    fecha_creacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    vigencia: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fecha_modificacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    clave: Mapped["Clave"] = relationship(back_populates="catalogos")
