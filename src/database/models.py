from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
    BigInteger,
)


Base = declarative_base()


class Flow(Base):
    """Учебный поток"""
    __tablename__ = 'flows'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    students = relationship("Student", 
                            back_populates="flow", 
                            cascade="all, delete-orphan")


class Student(Base):
    """Студент"""
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    flow_id = Column(Integer, ForeignKey('flows.id'), nullable=False)
    isu = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    chat_id = Column(BigInteger, nullable=True, unique=True)

    flow = relationship("Flow", back_populates="students")
    distribution = relationship("Distribution", 
                                back_populates="student", 
                                uselist=False, 
                                cascade="all, delete-orphan")


class Variant(Base):
    """Вариант"""
    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False, unique=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, unique=True)

    distributions = relationship("Distribution", 
                                 back_populates="variant", 
                                 cascade="all, delete-orphan")

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


class Teacher(Base):
    """Преподаватель"""
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)
