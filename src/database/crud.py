from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .models import Flow, Student, Variant
from .database import AsyncSession


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
        
        for title, flow in existing_flows.items():
            if title not in processed_flow_titles:
                flows_to_delete.add(title)
        
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
                existing_flows[flow_title] = flow
        
        await session.flush()
        
        for isu, full_name, flow_title in students:
            flow = existing_flows.get(flow_title)

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


async def get_all_variants():
    async with AsyncSession() as session:
        query = select(
            Variant.number,
            Variant.title,
            Variant.description
        )
        result = await session.execute(query)
        return result.all()


async def get_update_variants_info(variants):
    async with AsyncSession() as session:
        variants_result = await session.execute(select(Variant))
        existing_variants = {
            variant.number: variant 
            for variant in variants_result.scalars().all()
        }

        processed_variant_numbers = set()

        variants_to_add = set()
        variants_to_update = set()
        variants_to_delete = set()

        for number, title, description in variants:
            processed_variant_numbers.add(number)

            variant = existing_variants.get(number)
            if variant:
                if (variant.title != title or
                    variant.description != description):
                    variants_to_update.add((
                        variant.number,
                        variant.title,
                        variant.description,
                        title,
                        description
                    ))
            else:
                variants_to_add.add((number, title, description))
            
        for number, variant in existing_variants.items():
            if number not in processed_variant_numbers:
                variants_to_delete.add(
                    (number, variant.title, variant.description)
                )
        
        result = []

        if variants_to_add:
            result.append("Будут добавлены варианты:")
            for number, title, description in sorted(variants_to_add):
                result.append(f"№{number}. {title}\n\n{description}")
        
        if variants_to_update:
            result.append("Будут изменены варианты:")
            for number, old_title, old_description, \
                title, description in sorted(variants_to_update):
                result.append(
                    f'"""\n№{number}. {old_title}\n\n{old_description}\n"""' \
                    f'\n\n⬇️\n\n' \
                    f'"""\n№{number}. {title}\n\n{description}\n"""'
                )
        
        if variants_to_delete:
            result.append("Будут удалены варианты:")
            for number, title, description in sorted(variants_to_delete):
                result.append(f"№{number}. {title}\n\n{description}")
        
        return result


async def update_variants(variants):
    async with AsyncSession() as session:
        variants_result = await session.execute(select(Variant))
        existing_variants = {
            variant.number: variant 
            for variant in variants_result.scalars().all()
        }

        processed_variant_numbers = set()

        for number, title, description in variants:
            processed_variant_numbers.add(number)

            variant = existing_variants.get(number)
            if variant:
                if (variant.title != title or
                    variant.description != description):
                    variant.title = title
                    variant.description = description
            else:
                variant = Variant(
                    number=number,
                    title=title,
                    description=description
                )
                session.add(variant)
        
        variants_to_delete = [
            variant for number, variant in existing_variants.items()
            if number not in processed_variant_numbers
        ]
        for variant in variants_to_delete:
            await session.delete(variant)
        
        await session.commit()
