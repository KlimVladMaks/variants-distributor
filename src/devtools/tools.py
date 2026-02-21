# Запуск: python3 -m src.devtools.tools

from sqlalchemy import (
    update, 
    delete, 
    select,
)

from ..database.database import AsyncSession
from ..database.models import (
    Student, 
    Teacher, 
    Variant, 
    Distribution,
)


"""
Для запуска данных функция можно создать файл `src/devtools/use_tools.py`
(и добавить его в `.gitignore`):

```py
import asyncio

from . import tools


async def main():
    await tools.<нужная_функция>


if __name__ == "__main__":
    asyncio.run(main())

```

Запуска файла с помощью команд:
```
source .venv/bin/activate
python3 -m src.devtools.use_tools
```
"""


async def reset_all_chat_id():
    """Сбросить поле 'chat_id' у студентов и преподавателей"""
    async with AsyncSession() as session:
        await session.execute(
            delete(Teacher)
        )
        await session.execute(
            update(Student)
            .values(chat_id=None)
        )
        await session.commit()


async def set_new_variants_distribution(new_distribution):
    """
    Установить новое распределение вариантов среди студентов.

    new_distribution = {
        <номер_варианта>: [
            "<isu_студента>",
            "<isu_студента>",
            ...
        ],
        ...
    }
    (Номер варианта `-1` соответствует опции "Свой вариант")
    """
    async with AsyncSession() as session:
        students_result = await session.execute(select(Student))
        students = students_result.scalars().all()
        students_by_isu = {student.isu: student for student in students}

        variants_result = await session.execute(select(Variant))
        variants = variants_result.scalars().all()
        variants_by_number = {variant.number: variant for variant in variants}

        await session.execute(delete(Distribution))

        for variant_number, isu_list in new_distribution.items():
            for isu in isu_list:
                student = students_by_isu[isu]
                distribution = Distribution(student_id=student.id)
                if variant_number != -1:
                    variant = variants_by_number[variant_number]
                    distribution.variant_id = variant.id
                else:
                    distribution.variant_id = None
                session.add(distribution)
        
        await session.commit()
