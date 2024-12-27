from typing import Optional
from workspace_for_agents.actions import Action, Wait, parse_action
from workspace_for_agents.employee import Employee
from workspace_for_agents.file_system import File, Folder


class Agent(Employee):
    def __init__(
        self,
        available_actions: list[Action],
        agent_description: str = "An abstract Agent.",
    ):
        super().__init__(
            -1, "<agent>", "agent@company.com", "The agent that automates tasks."
        )
        self.available_actions = available_actions
        self.agent_description = agent_description
        self.header = ""
        self.env = None
        self.short_term_context: str = ""
        self.simlinks: dict[str, str] = {}

    @property
    def actions_descriptions(self) -> str:
        description = ""
        for action in self.available_actions:
            description += f"- {action.description()}\n"
        return description.strip()

    def add_to_download_folder(self, folder_or_file: File | Folder) -> None:
        download_folder_exists: bool = False
        self.simlinks[f"agent_downloads/{folder_or_file.name}/"] = folder_or_file.path
        for folder in self.folders:
            if folder.name == "agent_downloads":
                download_folder_exists = True
                download_folder = folder
                break

        if not download_folder_exists:
            download_folder = Folder("agent_downloads/", "agent_downloads")

        if isinstance(download_folder, File):
            file: File = folder_or_file
            download_folder.add_file(file)
        elif isinstance(download_folder, Folder):
            folder: Folder = folder_or_file
            download_folder.add_subfolder(folder)

        if not download_folder_exists:
            self.folders.append(download_folder)

    def choose_action(self) -> Action:
        return Wait()


class HumanAgent(Agent):
    def __init__(
        self,
        available_actions: list[Action],
        agent_description: str = "Human controlled-agent",
    ):
        super().__init__(available_actions, agent_description)

    def choose_action(self) -> Action:
        print(
            f"{self.short_term_context}\n\n{self.header}\n{self.actions_descriptions}"
        )
        action_string = input("> ")
        action = parse_action(action_string)
        self.short_term_context = ""
        return action
