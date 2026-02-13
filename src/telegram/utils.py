import csv
from io import StringIO


def parse_students_csv(file_content: bytes):
    """
    Парсит CSV-файл со студентами. Требуемый формат CSV-файла:
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
    reader = csv.reader(csv_file, delimiter=',')

    # Пропускаем заголовки
    next(reader)

    students = []
    for row in reader:
        strip_row = [cell.strip() for cell in row]
        isu, full_name, flow_title = strip_row[:3]
        students.append((isu, full_name, flow_title))
    
    return students
