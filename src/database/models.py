from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
)


Base = declarative_base()


class Flow(Base):
    """Учебный поток"""
    __tablename__ = 'flows'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    students = relationship("Student", back_populates="flow")


class Student(Base):
    """Студент"""
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    flow_id = Column(Integer, ForeignKey('flows.id'), nullable=False)
    isu = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)

    flow = relationship("Flow", back_populates="students")
    distribution = relationship("Distribution", back_populates="student", 
                                uselist=False)


class Variant(Base):
    """Вариант"""
    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False, unique=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, unique=True)

    distributions = relationship("Distribution", back_populates="variant")

    __table_args__ = (
        CheckConstraint('number > 0', name='check_number_positive'),
    )


class Distribution(Base):
    """Распределение вариантов среди студентов"""
    __tablename__ = 'distributions'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), 
                        nullable=False, unique=True)

    # Если variant_id == NULL, значит студент выбрал опцию "Свой вариант"
    variant_id = Column(Integer, ForeignKey('variants.id'), nullable=True)

    student = relationship("Student", back_populates="distribution")
    variant = relationship("Variant", back_populates="distributions")
