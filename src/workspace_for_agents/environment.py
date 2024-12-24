import json
from workspace_for_agents.actions import CheckMailBox, ReadMail, SendEmail, Wait
from workspace_for_agents.task import Task
from workspace_for_agents.agent import Agent, HumanAgent
from workspace_for_agents.employee import Employee


class Environment:
    def __init__(self, agent: Agent, employees: list[Employee] = []) -> None:
        self.employees = employees
        for employee in self.employees:
            employee.env = self
        self.agent = agent
        self.agent.env = self
        self.current_turn = 0
        self.current_states: list[str] = ["<default>"]

    def feed_fact(self, employee: Employee, fact: str):
        employee.known_facts.append(fact)

    def get_employee_by_name(self, name: str) -> Employee:
        for employee in self.employees:
            if employee.name == name:
                return employee

        raise KeyError(
            f"Couldn't find {name} when calling Environment.get_employee_by_name()"
        )

    def get_employee_by_email(self, email: str) -> Employee:
        if email == self.agent.email:
            return self.agent

        for employee in self.employees:
            if employee.email == email:
                return employee
        raise KeyError(
            f"Couldn't find {email} when calling Environment.get_employee_by_email()"
        )

    def display_relationships_graph(self):
        """Displays a graph visualization of employee relationships using networkx and matplotlib"""
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except ImportError:
            print("Error: This method requires networkx and matplotlib packages.")
            return

        # Create graph
        G = nx.Graph()

        # Add nodes (employees)
        for employee in self.employees:
            G.add_node(employee.id, name=employee.name)

        # Add edges (relationships)
        for employee in self.employees:
            for contact in employee.contacts:
                G.add_edge(employee.id, contact.id)

        # Set up the visualization
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)

        # Draw the network
        nx.draw(
            G,
            pos,
            with_labels=False,
            node_color="lightblue",
            node_size=500,
            font_size=10,
        )

        # Add labels with employee names
        labels = {node: G.nodes[node]["name"] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels)

        plt.title("Employee Relationships Network")
        plt.axis("off")
        plt.show()

    def run_task(self, task: Task, max_turns: int = 10) -> None:
        self.agent.header = task.task_goal
        for turn in range(max_turns):
            self.current_turn = turn
            action = self.agent.choose_action()
            self.agent.execute_action(action)

            for employee in self.employees:
                action = employee.choose_action()
                print(">", action)
                employee.execute_action(action)

        for goal in task.completion_goals:
            print(f"{goal.name}: {goal.score}")
        print(self.get_employee_by_email("ibrahim.mendoza@company.com").email_box)
        self.current_turn = 0


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

    for folder in env_data["folders"]:
        for employee_id in folder["has_access"]:
            employees[employee_id].add_files_from_folder(folder["path"])

    agent = HumanAgent(available_actions=[CheckMailBox, ReadMail, SendEmail, Wait])
    env = Environment(agent=agent, employees=list(employees.values()))
    return env
