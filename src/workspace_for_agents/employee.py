from dataclasses import dataclass
import os
from typing import Literal, Optional, Self

from openai import OpenAI
from pydantic import BaseModel, Field

from workspace_for_agents.mail import EmailBox
from workspace_for_agents.actions import Action, Wait, parse_action
from workspace_for_agents.file_system import File, Folder


class Employee:
    def __init__(
        self,
        id: int,
        name: str,
        email: str,
        additional_information: str,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.additional_information = additional_information
        self.contacts_map: dict[int, Self] = {}
        self.known_facts: list[str] = []
        self.folders: list[Folder] = []
        self.files: list[File] = []
        self.actions: list[Action] = []
        self.email_box = EmailBox()
        self.preplanned_actions: dict[str, Action] = {"do-nothing": Wait()}
        self.instructions: list[str] = []
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @property
    def formated_instructions(self):
        return "Instructions:\n" + "\n- ".join(self.instructions)

    def add_contact(self, employee: Self):
        if employee.id in self.contacts_map.keys():
            print(
                f"warning: {employee.id} is already mapped to {self.contacts_map[employee.id].name}. Therefore, {employee.name} was not added."
            )
        else:
            self.contacts_map[employee.id] = employee

    def add_files_from_folder(self, folder_path: str):
        import os

        # Create root folder
        folder_name = os.path.basename(folder_path)
        root_folder = Folder(folder_path, folder_name)
        self.folders.append(root_folder)

        # Walk through directory
        for dirpath, dirnames, filenames in os.walk(folder_path):
            # Create current folder
            current_folder = root_folder
            if dirpath != folder_path:
                rel_path = os.path.relpath(dirpath, folder_path)
                for folder_name in rel_path.split(os.sep):
                    new_folder = Folder(os.path.join(dirpath, folder_name), folder_name)
                    current_folder.add_subfolder(new_folder)
                    current_folder = new_folder

            # Add files in current folder
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file = File(file_path, filename)
                current_folder.add_file(file)
                self.files.append(file)

    @property
    def all_important_infos(self) -> str:
        infos = self.email_box.display()
        infos += "Mails details: \n\n"
        for email in self.email_box.emails:
            infos += email.string + "\n----\n"
        infos += "Available files:\n\n" + self.list_available_files()
        infos += "=====\nIMPORTANT\n====\nThese are the possible actions you can take this turn:"
        for id, preplanned_action in self.preplanned_actions.items():
            infos += f"ID: {id} ; description => {preplanned_action.description}\n\n"
        return infos

    def choose_action(self) -> Action:
        available_actions = tuple(list(self.preplanned_actions.keys()))

        class Choice(BaseModel):
            explanation: str = Field(description="The explaination behind your action.")
            choice_id: Literal[available_actions] = Field(
                description="The choice's id that you will take."
            )

        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": f"Your name is {self.name}. Here's more to know about you: {self.additional_information}\n\nAccording to the context, you will need to take an action.",
                },
                {"role": "user", "content": self.all_important_infos},
            ],
            response_format=Choice,
        )

        choice_taken_by_employee = completion.choices[0].message.parsed
        print(">>>>>>>>", choice_taken_by_employee)
        if "send-mail-agent-need-hire" in self.preplanned_actions.keys():
            return self.preplanned_actions["send-mail-agent-need-hire"]
        return Wait()

    def execute_action(self, action: Action):
        action.source = self
        action.execute(self.env)
        self.actions.append(action)

    @property
    def contacts(self):
        return list(self.contacts_map.values())

    def list_available_files(self) -> str:
        all_trees = ""
        for folder in self.folders:
            all_trees += folder.tree() + "\n"
        return all_trees

    def __repr__(self) -> str:
        return f"Employee(id={self.id}, name={self.name}, email={self.email}, additional_info={self.additional_information})"
