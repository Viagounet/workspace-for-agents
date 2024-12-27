from dataclasses import dataclass
import json
import os
from typing import Any
from workspace_for_agents.actions import (
    CheckMailBox,
    DisplayContacts,
    DisplayFiles,
    ReadMail,
    ReadMarkdownFile,
    ReadPDFPage,
    SendEmail,
    SetTaskAsCompleted,
    Wait,
)
from workspace_for_agents.task import Task
from workspace_for_agents.agent import Agent, GPTAgent, HumanAgent
from workspace_for_agents.employee import Employee


@dataclass
class Log:
    log_type: str
    turn: int
    emitted_by: str
    content: dict[str, Any]

    @property
    def json(self):
        return {
            "log_type": self.log_type,
            "turn": self.turn,
            "emitted_by": self.emitted_by,
            "content": self.content,
        }


class Environment:
    def __init__(self, agent: Agent, employees: list[Employee] = []) -> None:
        self.employees = employees
        for employee in self.employees:
            employee.env = self
        self.agent = agent
        self.agent.env = self
        self.current_turn = 0
        self.current_states: list[str] = ["<default>"]
        self.logs: list[Log] = []

    def add_log(self, log_type: str, emitted_by: str, content: dict[str, Any]):
        self.logs.append(Log(log_type, self.current_turn, emitted_by, content))

    def save_logs(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([log.json for log in self.logs], f, ensure_ascii=False, indent=4)

    def feed_fact(self, employee: Employee, fact: str):
        employee.known_facts.append(fact)

    def get_employees_by_tag(self, tags: list[str]) -> list[Employee]:
        employees = []
        for employee in self.employees:
            for tag in employee.tags:
                if tag.lower() in [tag.lower() for tag in tags]:
                    employees.append(employee)
                    break
        return employees

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

    def run_task(self, task: Task, max_turns: int = 100) -> None:
        self.agent.header = f"High-level objective: {task.task_goal}"
        task_ongoing = True
        for turn in range(max_turns):
            action = None
            while not isinstance(action, Wait) and task_ongoing:
                action = self.agent.choose_action()
                self.agent.execute_action(action)
                if os.environ["LOG_ACTIONS"] == "True":
                    self.add_log(
                        "action",
                        self.agent.name,
                        content={
                            "action_name": action.__class__.__name__,
                            "content": action.json,
                        },
                    )

                if os.getenv("LOGS"):
                    self.save_logs(path="logs.json")

                if isinstance(action, SetTaskAsCompleted):
                    task_ongoing = False
            if task_ongoing == False:
                break
            for employee in self.employees:
                actions = employee.choose_actions()
                for action in actions:
                    employee.execute_action(action)
                    if os.environ["LOG_ACTIONS"] == "True":
                        self.add_log(
                            "action",
                            employee.name,
                            content={
                                "action_name": action.__class__.__name__,
                                "content": action.json,
                            },
                        )
                    if os.getenv("LOGS"):
                        self.save_logs(path="logs.json")
                    if isinstance(action, SetTaskAsCompleted):
                        task_ongoing = False
                        break

            for goal in task.completion_goals:
                if goal.score == 1 and goal.triggers_completion:
                    task_ongoing = False

            if task_ongoing == False:
                break

            self.current_turn += 1

        for goal in task.completion_goals:
            print(f"{goal.name}: {goal.score}")
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
            tags=employee_info["tags"],
        )

    # Setting up relationships
    for employee_info in env_data["employees"]:
        employee = employees[employee_info["id"]]
        for contact_id in employee_info["contacts_ids"]:
            employee.add_contact(employees[contact_id])

    for folder in env_data["folders"]:
        for employee_id in folder["has_access"]:
            employees[employee_id].add_files_from_folder(folder["path"])

    agent = GPTAgent(
        available_actions=[
            DisplayContacts,
            CheckMailBox,
            ReadMail,
            SendEmail,
            DisplayFiles,
            ReadPDFPage,
            ReadMarkdownFile,
            Wait,
            SetTaskAsCompleted,
        ]
    )
    env = Environment(agent=agent, employees=list(employees.values()))
    return env
