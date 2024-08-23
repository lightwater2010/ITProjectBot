from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, Table, ForeignKey, Column
from typing import Annotated

pk = Annotated[int, mapped_column(primary_key=True)]
tg_id = Annotated[int, mapped_column(BigInteger)]
class Base(DeclarativeBase, AsyncAttrs):
    pass


programmer_project_table = Table(
    'programmer_project', Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('programmer_id', ForeignKey('programmers.id'), primary_key=True)
)
class Programmer(Base):
    __tablename__ = "programmers"
    id: Mapped[pk]
    name:Mapped[str]
    description: Mapped[str]
    exception: Mapped[str]
    user_name: Mapped[str]
    projects: Mapped[list["Project"]] = relationship('Project', secondary=programmer_project_table, back_populates='programmers')
    tg_id: Mapped[tg_id]

class Project(Base):
    __tablename__ = "projects"
    id:Mapped[pk]
    project_name:Mapped[str]
    description:Mapped[str]
    places:Mapped[int]
    occupied_places:Mapped[int]
    free_places:Mapped[int]
    required_skills:Mapped[str]
    user_name: Mapped[str]
    programmers: Mapped[list["Programmer"]] = relationship('Programmer', secondary=programmer_project_table, back_populates="projects")
    tg_id: Mapped[tg_id]




