from workspace_for_agents.actions import Action, Wait
from workspace_for_agents.employee import Employee


class Agent(Employee):
    def __init__(self, agent_description: str = "An abstract Agent."):
        super().__init__(-1, "<agent>", "agent@company.com", "The agent that automates tasks.")
        self.agent_description = agent_description
    def execute(self) -> Action:
        return Wait()