from workspace_for_agents.employee import Employee


class Environnement:
    def __init__(self, employees: list[Employee] = []) -> None:
        self.employees = employees

    def feed_fact(self, employee: Employee, fact: str):
        employee.known_facts.append(fact)
