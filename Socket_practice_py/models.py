from sqlalchemy import String, create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped


# engine = create_engine("sqlite://", echo=True)
class Base(DeclarativeBase):
    pass

class Usuarios(Base):
    __tablename__ = "Usuarios"
    # Clave primaria autoincremental 
    id: Mapped[int] = mapped_column(primary_key=True)
    # Declaracion de atributos
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Retorna los atributos del objeto
    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, username={self.username})>"


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
print(CreateTable(Usuarios.__table__).compile(engine))