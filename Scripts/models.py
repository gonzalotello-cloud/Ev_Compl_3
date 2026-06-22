from typing import Optional
from sqlmodel import Field, SQLModel

# Tabla categoría
class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, nullable=False)

# Tabla Libro
class Libro(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(unique=True, nullable=False)
    precio: float = Field(gt=0)
    valoracion: int = Field(
        ge=1,
        le=5,
    )
    # Por defecto se considerará que un libro no tiene stock
    disponible: bool = Field(default=False)
    url_detalle: Optional[str] = Field(default=None, nullable=True)

    # Clave foránea a categoría
    categoria_id: int = Field(foreign_key="categoria.id")


