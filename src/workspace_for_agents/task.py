from typing import TypedDict
from workspace_for_agents.employee import Employee


class Goal:
    def __init__(self, name: str, conditions) -> None:
        self.name = name
        self.conditions = conditions

    @property
    def score(self):
        points = 0
        for condition in self.conditions:
            if condition():  # Call the condition function to evaluate it dynamically
                points += 1
        return points / len(self.conditions)


class Behaviour:
    def __init__(self, employee: Employee, conditions: dict[list[str], str]) -> None:
        self.employee = employee
        self.conditions = conditions


class Task:
    def __init__(
        self,
        task_id: str,
        task_goal: str,
        completion_goals: list[Goal],
        behaviours: list[Behaviour],
    ) -> None:
        self.task_id = task_id
        self.task_goal = task_goal
        self.completion_goals = completion_goals
        self.behaviours = behaviours

    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, goal={self.task_goal}, goals={len(self.completion_goals)}, behaviours={len(self.behaviours)})"

    def __str__(self) -> str:
        return f"Task {self.task_id}: {self.task_goal}"
