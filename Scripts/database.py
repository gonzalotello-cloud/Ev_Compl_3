from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from pathlib import Path

# Definición del nombre de la base de datos y ubicación
# DB se almacenará en data/processed
BASEDATOS: Path = Path(__file__).parent.parent / "data" / "processed" / "data.db"
BASEDATOS_URL: str = f"sqlite:///{BASEDATOS}"


# Creación del engine
engine = create_engine(
    BASEDATOS_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # Requerido para SQLite
)

# Crea las tablas según lo indicado en models.py
def crear_tablas() -> None:
    SQLModel.metadata.create_all(engine)

# Crea una sesión lista para usar y la cierra al terminar
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session