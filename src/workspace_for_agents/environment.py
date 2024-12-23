import json
from workspace_for_agents.employee import Employee


class Environment:
    def __init__(self, employees: list[Employee] = []) -> None:
        self.employees = employees

    def feed_fact(self, employee: Employee, fact: str):
        employee.known_facts.append(fact)


def create_environnement_from_file(file_path: str) -> Environment:
    with open(file_path, "r", encoding="utf-8") as f:
        env_data = json.load(f)

    employees: dict[int, Employee] = {}
    for employee_info in env_data["employees"]:
        employees[employee_info["id"]] = Employee(
            id=employee_info["id"],
            name=employee_info["name"],
            email=employee_info["email"],
            additional_information=employee_info["additional_information"],
        )

    # Setting up relationships
    for employee_info in env_data["employees"]:
        employee = employees[employee_info["id"]]
        for contact_id in employee_info["contacts_ids"]:
            employee.add_contact(employees[contact_id])

    env = Environment(employees=list(employees.values()))
    return env
