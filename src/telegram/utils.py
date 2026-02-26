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
