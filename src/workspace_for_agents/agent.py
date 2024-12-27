import os
from typing import Optional

from pydantic import BaseModel, Field
from workspace_for_agents.actions import Action, Wait, parse_action
from workspace_for_agents.employee import Employee
from workspace_for_agents.file_system import File, Folder
from workspace_for_agents.llm_client import client


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


class ReActElement(BaseModel):
    reasoning: str = Field(description="The reasoning behind the function call")
    function_call: str = Field(
        description="The function to call & the appropriate arguments to achieve your action"
    )


class GPTAgent(Agent):
    def __init__(
        self,
        available_actions: list[Action],
        agent_description: str = "An abstract Agent.",
    ):
        super().__init__(available_actions, agent_description)
        self.history: list[str] = []

    def choose_action(self) -> Action:
        history_string = "LAST ACTIONS: \n\n" + "\n".join(self.history)
        prompt = f"{history_string}\n\n===CURRENT TURN===\n\n{self.short_term_context}\n\n{self.header}\n{self.actions_descriptions}"
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are <Agent> (agent@company.com), a helpful assistant that tries to help a company. You will be given a high-level goal to achieve, as well as functions to call. You must execute the appropriate actions to achieve the overarching objective. Note: the actions will actually take place only after calling wait().",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=ReActElement,
        )
        react_response = completion.choices[0].message.parsed
        if hasattr(self, "env") and os.environ["LOG_CALLS"] == "True":
            self.env.add_log(
                "react_response",
                self.name,
                content={
                    "prompt": prompt,
                    "reasoning": react_response.reasoning,
                    "function_call": react_response.function_call,
                },
            )

        history_log = str(
            {
                "reasoning": react_response.reasoning,
                "function_call": react_response.function_call,
                "function_output": self.short_term_context,
            }
        )
        action = parse_action(react_response.function_call)
        self.history.append(history_log)
        self.short_term_context = ""
        return action
