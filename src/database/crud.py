from sqlalchemy import select
from sqlalchemy.sql import join

from .models import Flow, Student, Variant
from .database import AsyncSession


async def save_students(students):
    """Сохранить студентов и их потоки в БД"""
    async with AsyncSession() as session:
        flows_cache = {}

        for isu, full_name, flow_title in students:
            if flow_title not in flows_cache:
                query = select(Flow).where(Flow.title == flow_title)
                result = await session.execute(query)
                flow = result.scalar_one_or_none()

                if not flow:
                    flow = Flow(title=flow_title)
                    session.add(flow)
                    await session.flush()
                
                flows_cache[flow_title] = flow

            student = Student(
                isu=isu,
                full_name=full_name,
                flow_id=flows_cache[flow_title].id
            )
            session.add(student)
        
        await session.commit()


async def get_all_students_with_flows():
    """Получить всех студентов с их потоками"""
    async with AsyncSession() as session:
        query = select(
            Student.isu,
            Student.full_name,
            Flow.title
        ).join(Flow, Student.flow_id == Flow.id)
        result = await session.execute(query)
        return result.all()


async def save_variants(variants):
    async with AsyncSession() as session:
        for number, title, description in variants:
            variant = Variant(
                number=number,
                title=title,
                description=description
            )
            session.add(variant)
        await session.commit()


async def get_all_variants():
    async with AsyncSession() as session:
        query = select(
            Variant.number,
            Variant.title,
            Variant.description
        )
        result = await session.execute(query)
        return result.all()
