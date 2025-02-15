import os
from typing import Self


from workspace_for_agents.mail import EmailBox
from workspace_for_agents.actions import Action, ConditionedAction
from workspace_for_agents.file_system import File, Folder


class Employee:
    def __init__(
        self,
        id: int,
        name: str,
        email: str,
        additional_information: str,
        tags: list[str] = [],
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
        self.tags = tags

    @property
    def formated_instructions(self):
        return "Instructions:\n" + "\n- ".join(self.instructions)

    @property
    def formated_contacts(self):
        contacts = "Contacts:\n\n"
        for id, contact_info in self.contacts_map.items():
            contacts += f"- {contact_info.name} - {contact_info.additional_information} (email: {contact_info.email})\n"
        return contacts

    def add_contact(self, employee: Self):
        if employee.id in self.contacts_map.keys():
            print(
                f"warning: {employee.id} is already mapped to {self.contacts_map[employee.id].name}. Therefore, {employee.name} was not added."
            )
        else:
            self.contacts_map[employee.id] = employee

    def add_files_from_folder(self, folder_path: str):
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
        infos = ""
        infos += f"<Mails>\n{self.email_box.display_all_in_chronological_order()}\n</Mails>\n"
        infos += (
            f"<Available files>\n{self.list_available_files()}\n</Available files>\n"
        )
        infos += (
            f"<Known contacts>\n{self.formated_contacts}\n</Known contacts>\n\n===\n\n"
        )
        infos += f"General instructions for interacting with the agent: \n\n{self.formated_instructions}"
        return infos

    def choose_actions(self) -> list[Action]:
        actions: list[Action] = []
        for id, preplanned_action in self.preplanned_actions.items():
            all_requirements_completed = True
            for required_completed_actions in preplanned_action.requires_completion:
                if not required_completed_actions.is_completed:
                    all_requirements_completed = False
                    break
            if not all_requirements_completed:
                continue

            if hasattr(self, "env") and os.environ["LOG_CONDITIONS"] == "True":
                self.env.add_log(
                    "preplanned_action_cond",
                    self.name,
                    preplanned_action.condition._evaluate(),
                )
            if (
                not preplanned_action.is_completed
                or preplanned_action.stays_after_completion
            ) and preplanned_action.condition.is_true():
                actions.append(preplanned_action.linked_action)
                preplanned_action.is_completed = True
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
