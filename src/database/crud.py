from sqlalchemy import select
from sqlalchemy.orm import selectinload

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


async def get_update_students_info(students):
    async with AsyncSession() as session:
        flows_result = await session.execute(select(Flow))
        existing_flows = {
            flow.title: flow for flow in flows_result.scalars().all()
        }

        students_result = await session.execute(
            select(Student).options(selectinload(Student.flow))
        )
        existing_students = {
            student.isu: student for student in students_result.scalars().all()
        }

        processed_flow_titles = set()
        processed_student_isus = set()

        flows_to_add = set()
        flows_to_delete = set()

        students_to_add = set()
        students_to_update = set()
        students_to_delete = set()

        for isu, full_name, flow_title in students:
            processed_student_isus.add(isu)
            processed_flow_titles.add(flow_title)

            flow = existing_flows.get(flow_title)
            if not flow:
                flows_to_add.add(flow_title)
            
            student = existing_students.get(isu)
            if student:
                if (student.full_name != full_name or 
                    student.flow.title != flow_title):
                    students_to_update.add((
                        isu,
                        student.full_name,
                        student.flow.title,
                        full_name,
                        flow_title
                    ))
            else:
                students_to_add.add((isu, full_name, flow_title))
            
        for isu, student in existing_students.items():
            if isu not in processed_student_isus:
                students_to_delete.add(
                    (isu, student.full_name, student.flow.title)
                )
        
        for title in existing_flows.items():
            if title not in processed_flow_titles:
                flows_to_delete(flow_title)
        
        result = []

        if students_to_add:
            block = "Будут добавлены студенты:\n\n"
            for isu, full_name, flow_title in sorted(
                students_to_add,
                key=lambda x: x[1]
            ):
                block += f"{isu}, {full_name}, {flow_title}\n"
            result.append(block.rstrip('\n'))
        
        if students_to_update:
            block = "Будут изменены данные студентов:\n\n"
            for isu, old_name, old_flow, new_name, new_flow in sorted(
                students_to_update,
                key=lambda x: x[3]
            ):
                block += f"{isu}, ({new_name}, {new_flow} <- " \
                         f"{old_name}, {old_flow})\n"
            result.append(block.rstrip('\n'))
        
        if students_to_delete:
            block = "Будут удалены студенты:\n\n"
            for isu, full_name, flow_title in sorted(
                students_to_delete,
                key=lambda x: x[1]
            ):
                block += f"{isu}, {full_name}, {flow_title}\n"
            result.append(block.rstrip('\n'))
        
        if flows_to_add:
            block = "Будут добавлены потоки:\n\n"
            for title in sorted(flows_to_add):
                block += f"{title}\n"
            result.append(block.rstrip('\n'))
        
        if flows_to_delete:
            block = "Будут удалены потоки:\n\n"
            for title in sorted(flows_to_delete):
                block += f"{title}\n"
            result.append(block.rstrip('\n'))
        
        return result


async def update_students(students):
    async with AsyncSession() as session:
        flows_result = await session.execute(select(Flow))
        existing_flows = {
            flow.title: flow for flow in flows_result.scalars().all()
        }

        students_result = await session.execute(select(Student))
        existing_students = {
            student.isu: student for student in students_result.scalars().all()
        }

        processed_flow_titles = set()
        processed_student_isus = set()

        for isu, full_name, flow_title in students:
            processed_student_isus.add(isu)
            processed_flow_titles.add(flow_title)

            flow = existing_flows.get(flow_title)
            if not flow:
                flow = Flow(title=flow_title)
                session.add(flow)
                await session.flush()
                existing_flows[flow_title] = flow
            
            student = existing_students.get(isu)
            if student:
                if (student.full_name != full_name or 
                    student.flow_id != flow.id):
                    student.full_name = full_name
                    student.flow_id = flow.id
            else:
                student = Student(
                    isu=isu,
                    full_name=full_name,
                    flow_id=flow.id
                )
                session.add(student)
            
        students_to_delete = [
            student for isu, student in existing_students.items() 
            if isu not in processed_student_isus
        ]
        for student in students_to_delete:
            await session.delete(student)
        
        await session.flush()

        flows_to_delete = [
            flow for title, flow in existing_flows.items()
            if title not in processed_flow_titles 
        ]
        for flow in flows_to_delete:
            await session.delete(flow)
        
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
