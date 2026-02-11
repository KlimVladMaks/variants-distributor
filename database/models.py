from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)


Base = declarative_base()


class Flow(Base):
    """Учебный поток"""
    __tablename__ = 'flows'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)


class Student(Base):
    """Студент"""
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey('flows.id'), nullable=False)
    isu = Column(String, nullable=False)
    full_name = Column(String, nullable=False)


class Variant(Base):
    """Вариант"""
    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)


class Distribution(Base):
    """Распределение вариантов среди студентов"""
    __tablename__ = 'distributions'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)

    # Если variant_id == NULL, значит студент выбрал опцию "Свой вариант"
    variant_id = Column(Integer, ForeignKey('variants.id'), nullable=True)
