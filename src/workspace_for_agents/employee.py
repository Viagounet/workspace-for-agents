import os
from typing import Literal, Self

from openai import OpenAI
from pydantic import BaseModel, Field

from workspace_for_agents.mail import EmailBox
from workspace_for_agents.actions import Action, ConditionedAction, Wait
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
        self.preplanned_actions: dict[str, ConditionedAction] = {}
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
        return infos

    def choose_actions(self) -> list[Action]:
        actions: list[Action] = []
        actions_ids: list[str] = []
        for id, preplanned_action in self.preplanned_actions.items():
            if preplanned_action["condition"]():
                actions.append(preplanned_action["linked_action"])
                actions_ids.append(id)
        for id in actions_ids:
            del self.preplanned_actions[id]
        return actions

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
