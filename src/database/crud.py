from math import ceil
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import (
    selectinload, 
    joinedload, 
)
from datetime import datetime

from .models import (
    Flow, 
    Student, 
    Variant, 
    Distribution,
    Teacher,
)
from .database import AsyncSession


# ====================
# ===== Студенты =====
# ====================


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
            result.append("Будут добавлены студенты:")
            block = ""
            for isu, full_name, flow_title in sorted(
                students_to_add,
                key=lambda x: (x[2], x[1])
            ):
                block += f"{isu}, {full_name}, {flow_title}\n"
            result.append(block.rstrip('\n'))
        
        if students_to_update:
            result.append("Будут изменены данные студентов:")
            block = ""
            for isu, old_name, old_flow, new_name, new_flow in sorted(
                students_to_update,
                key=lambda x: (x[4], x[3])
            ):
                block += f"{isu}, ({new_name}, {new_flow} <- " \
                         f"{old_name}, {old_flow})\n"
            result.append(block.rstrip('\n'))
        
        if students_to_delete:
            result.append("Будут удалены студенты:")
            block = ""
            for isu, full_name, flow_title in sorted(
                students_to_delete,
                key=lambda x: (x[2], x[1])
            ):
                block += f"{isu}, {full_name}, {flow_title}\n"
            result.append(block.rstrip('\n'))
        
        if flows_to_add:
            result.append("Будут добавлены потоки:")
            block = ""
            for title in sorted(flows_to_add):
                block += f"{title}\n"
            result.append(block.rstrip('\n'))
        
        if flows_to_delete:
            result.append("Будут удалены потоки:")
            block = ""
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


async def update_student_chat_id(isu, new_chat_id):
    async with AsyncSession() as session:
        result = await session.execute(
            select(Student)
            .where(Student.isu == isu)
        )
        student = result.scalar_one()
        student.chat_id = new_chat_id
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


async def get_student_by_isu(isu: str) -> Optional[Student]:
    async with AsyncSession() as session:
        query = (
            select(Student)
            .options(
                joinedload(Student.flow),
                joinedload(Student.distribution)
                .joinedload(Distribution.variant)
            )
            .where(Student.isu == isu)
        )
        student = await session.execute(query)
        return student.scalar_one_or_none()


async def get_student_by_chat_id(chat_id: int) -> Optional[Student]:
    async with AsyncSession() as session:
        query = (
            select(Student)
            .options(
                joinedload(Student.flow),
                joinedload(Student.distribution)
                .joinedload(Distribution.variant)
            )
            .where(Student.chat_id == chat_id)
        )
        student = await session.execute(query)
        return student.scalar_one_or_none()


# ====================
# ===== Варианты =====
# ====================


async def get_update_variants_info(variants_data):
    variants = []
    for number, title, description in variants_data:
        variants.append((int(number), title, description))

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


async def update_variants(variants_data):
    variants = []
    for number, title, description in variants_data:
        variants.append((int(number), title, description))

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


async def get_all_variants():
    async with AsyncSession() as session:
        query = select(
            Variant.number,
            Variant.title,
            Variant.description
        )
        result = await session.execute(query)
        return result.all()


async def get_variant_by_number(number: int) -> Optional[Variant]:
    async with AsyncSession() as session:
        variant = await session.execute(
            select(Variant)
            .where(Variant.number == number)
        )
        return variant.scalar_one_or_none()


# ===============================
# ===== Студенты и варианты =====
# ===============================


async def get_variants_info_for_student(chat_id: int):
    async with AsyncSession() as session:
        student = await session.execute(
            select(Student)
            .where(Student.chat_id == chat_id)
            .options(selectinload(Student.flow))
        )
        student = student.scalar_one_or_none()

        students = await session.execute(
            select(Student)
            .where(Student.flow_id == student.flow_id)
            .options(selectinload(Student.distribution))
        )
        students = students.scalars().all()

        variants = await session.execute(
            select(Variant).order_by(Variant.number)
        )
        variants = variants.scalars().all()

        total_students = len(students)
        limit_per_variant = ceil(total_students / len(variants))

        taken_counts = {v.id: 0 for v in variants}
        for s in students:
            if s.distribution and s.distribution.variant_id:
                taken_counts[s.distribution.variant_id] += 1
        
        unavailable = []
        available = []

        for variant in variants:
            taken = taken_counts[variant.id]
            free = limit_per_variant - taken
            is_available = free > 0

            message = (
                f"№{variant.number} {'✅' if is_available else '❌'}\n\n"
                f"Свободных мест: {free}/{limit_per_variant}\n\n"
                f"{variant.title}\n\n"
                f"{variant.description}"
            )

            if is_available:
                available.append((variant.number, variant, message))
            else:
                unavailable.append((variant.number, variant, message))

        return unavailable, available


async def update_student_variant(chat_id: int, 
                                 variant_number: Optional[int] = None) -> int:
    """
    Коды возврата:
    0 - вариант студента успешно обновлён.
    1 - данный вариант уже занят.

    При variant_number=None вариант студента просто сбрасывается.
    """
    async with AsyncSession() as session:
        student = await session.execute(
            select(Student)
            .where(Student.chat_id == chat_id)
            .options(selectinload(Student.flow))
        )
        student = student.scalar_one_or_none()

        students = await session.execute(
            select(Student)
            .where(Student.flow_id == student.flow_id)
            .options(selectinload(Student.distribution))
        )
        students = students.scalars().all()

        variants = await session.execute(select(Variant))
        variants = variants.scalars().all()

        if variant_number is None:
            if student.distribution:
                await session.delete(student.distribution)
                await session.commit()
            return 0

        if variant_number == -1:
            if student.distribution:
                student.distribution.variant_id = None
            else:
                distribution = Distribution(
                    student_id=student.id,
                    variant_id=None
                )
                session.add(distribution)
            await session.commit()
            return 0
        
        target_variant = None
        for variant in variants:
            if variant.number == variant_number:
                target_variant = variant
                break
        
        total_students = len(students)
        limit_per_variant = ceil(total_students / len(variants))

        variant_counts = {v.id: 0 for v in variants}
        for s in students:
            if s.distribution and s.distribution.variant_id:
                variant_counts[s.distribution.variant_id] += 1
        
        current_count = variant_counts[target_variant.id]
        if current_count >= limit_per_variant:
            return 1
        
        if student.distribution:
            student.distribution.variant_id = target_variant.id
        else:
            distribution = Distribution(
                student_id=student.id,
                variant_id=target_variant.id
            )
            session.add(distribution)
        
        await session.commit()
        return 0


# =========================
# ===== Google Sheets =====
# =========================


async def get_students_data_for_google_sheets():
    async with AsyncSession() as session:
        flows_query = (
            select(Flow)
            .options(
                selectinload(Flow.students)
                .selectinload(Student.distribution)
                .selectinload(Distribution.variant)
            )
            .order_by(Flow.title)
        )
        result = await session.execute(flows_query)
        flows = result.scalars().all()

        report = []

        now = datetime.now()
        report.append(["Обновлено:", now.strftime("%Y-%m-%d %H:%M:%S")])

        report.append(["isu", "full_name", "variant_number", "variant_title"])

        for flow in flows:
            report.append([flow.title])

            sorted_students = sorted(flow.students, key=lambda s: s.full_name)
            for student in sorted_students:
                student_data = [student.isu, student.full_name]
                if student.distribution and student.distribution.variant:
                    student_data.extend([
                        student.distribution.variant.number,
                        student.distribution.variant.title
                    ])
                elif student.distribution and student.distribution.variant_id is None:
                    student_data.extend([-1, "Свой вариант"])
                report.append(student_data)
        
        return report


async def get_variants_data_for_google_sheets():
    async with AsyncSession() as session:
        flows_query = (
            select(Flow)
            .options(
                selectinload(Flow.students)
                .selectinload(Student.distribution)
            )
            .order_by(Flow.title)
        )
        flows = await session.execute(flows_query)
        flows = flows.scalars().all()

        variants_query = select(Variant).order_by(Variant.number)
        variants = await session.execute(variants_query)
        variants = variants.scalars().all()

        report = []

        now = datetime.now()
        report.append(["Обновлено:", now.strftime("%Y-%m-%d %H:%M:%S")])

        report.append(["number", "title", "taken", "limit", "percent"])

        for flow in flows:
            report.append([flow.title])

            flow_students = flow.students
            total_students = len(flow_students)
            variants_count = len(variants)
            limit_per_variant = ceil(total_students / variants_count)

            custom_variant_students = [
                s for s in flow_students 
                if s.distribution and s.distribution.variant_id is None
            ]
            custom_variant_count = len(custom_variant_students)
            report.append([-1, "Свой вариант", custom_variant_count])

            for variant in variants:
                students_with_variant = [
                    s for s in flow_students 
                    if s.distribution and s.distribution.variant_id == variant.id
                ]
                taken_count = len(students_with_variant)
                percent = f"{int((taken_count / limit_per_variant) * 100)}%"
                report.append([
                    variant.number,
                    variant.title,
                    taken_count,
                    limit_per_variant,
                    percent
                ])
            
        return report


# =========================
# ===== Преподаватели =====
# =========================


async def is_teacher_chat_id(chat_id: int) -> bool:
    async with AsyncSession() as session:
        teacher = await session.execute(
            select(Teacher)
            .where(Teacher.chat_id == chat_id)
        )
        teacher = teacher.scalar_one_or_none()
        return True if teacher else False


async def add_teacher_chat_id(new_chat_id):
    async with AsyncSession() as session:
        teacher = Teacher(chat_id=new_chat_id)
        session.add(teacher)
        await session.commit()
