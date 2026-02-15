import csv
from io import StringIO


def parse_students_csv(file_content: bytes):
    """
    Парсит CSV-файл со студентами.
    Требуемый формат CSV-файла:
    ```csv
    isu,full_name,flow_title
    568526,Иванов Дмитрий Александрович,БР1
    698258,Петрова Анна Сергеевна,БР1
    785625,Алексеев Игорь Николаевич,БР2
    ...
    ```
    Формат вывода:
    ```py
    [
        ("568526", "Иванов Дмитрий Александрович", "БР1"),
        ("698258", "Петрова Анна Сергеевна", "БР1"),
        ("785625", "Алексеев Игорь Николаевич", "БР2"),
        ...
    ]
    ```
    """
    csv_text = file_content.decode('utf-8-sig')
    csv_file = StringIO(csv_text)

    # Определяем тип CSV-разделителя
    first_line = csv_file.readline()
    if ';' in first_line:
        delimiter = ';'
    else:
        delimiter = ','
    
    reader = csv.reader(csv_file, delimiter=delimiter)

    students = []
    for row in reader:
        strip_row = [cell.strip() for cell in row]
        isu, full_name, flow_title = strip_row[:3]
        students.append((isu, full_name, flow_title))
    
    return students


def parse_variants_csv(file_content: bytes):
    csv_text = file_content.decode('utf-8-sig')
    csv_file = StringIO(csv_text)
    
    # Определяем тип CSV-разделителя
    first_line = csv_file.readline()
    if ';' in first_line:
        delimiter = ';'
    else:
        delimiter = ','
    
    reader = csv.reader(csv_file, delimiter=delimiter)

    variants = []
    for row in reader:
        strip_row = [cell.strip() for cell in row]
        number, title, description = strip_row[:3]
        variants.append((int(number), title, description))
    
    return variants


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
        students_str = "\n".join(
            f"{isu}, {full_name}" 
            for isu, full_name in sorted_students
        )
        result.append((flow, students_str))
    
    return result
