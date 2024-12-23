from workspace_for_agents.actions import Action, Wait, parse_action
from workspace_for_agents.employee import Employee


class Agent(Employee):
    def __init__(self, available_actions: list[Action], agent_description: str = "An abstract Agent."):
        super().__init__(
            -1, "<agent>", "agent@company.com", "The agent that automates tasks."
        )
        self.available_actions = available_actions
        self.agent_description = agent_description
        self.header = ""

    @property
    def actions_descriptions(self) -> str:
        description = ""
        for action in self.available_actions:
            description += f"- {action.description()}\n"
        return description.strip()

    def execute_action(self, action: Action):
        action.source = self
        action.execute()

    def choose_action(self) -> Action:
        return Wait()

class HumanAgent(Agent):
    def __init__(self, available_actions: list[Action], agent_description: str = "Human controlled-agent"):
        super().__init__(available_actions, agent_description)

    def choose_action(self) -> Action:
        print(f"{self.header}\n{self.actions_descriptions}")
        action_string = input("> ")
        action = parse_action(action_string)
        return action