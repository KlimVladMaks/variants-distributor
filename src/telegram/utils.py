from aiogram.types import Message


def format_students_by_flows(students):
    flows = {}
    for student in students:
        isu, full_name, flow = student
        if flow not in flows:
            flows[flow] = []
        flows[flow].append((isu, full_name))
    
    result = []
    for flow in sorted(flows.keys()):
        sorted_students = sorted(flows[flow], key=lambda x: x[1])
        students_count = len(sorted_students)
        students_str = "\n".join(
            f"{isu}, {full_name}" 
            for isu, full_name in sorted_students
        )
        result.append((flow, students_count, students_str))
    
    return result


async def safe_message_answer(message: Message, text: str, reply_markup=None):
    """
    Безопасная отправка потенциально длинных сообщений. Если сообщение слишком 
    длинное, то оно отправляется в виде нескольких сообщений
    """
    MAX_LENGTH = 4000

    if len(text) <= MAX_LENGTH:
        await message.answer(text, reply_markup=reply_markup)
        return

    parts = []
    for i in range(0, len(text), MAX_LENGTH):
        part = text[i:i + MAX_LENGTH]
        parts.append(part)
    
    for i, part in enumerate(parts):
        current_markup = reply_markup if i == len(parts) - 1 else None
        await message.answer(part, reply_markup=current_markup)
