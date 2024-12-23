from typing import Self

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
    def contacts(self):
        return list(self.contacts_map.values())

    def list_available_files(self):
        for folder in self.folders:
            print(folder.tree())

    def __repr__(self) -> str:
        return f"Employee(id={self.id}, name={self.name}, email={self.email}, additional_info={self.additional_information})"
