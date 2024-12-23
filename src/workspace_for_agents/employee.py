from typing import Self


class Employee:
    def __init__(self, id: int, name: str, email: str, contacts_map: dict[int, Self], additional_information: str):
        self.id = id
        self.name = name
        self.contacts_map = contacts_map
        self.known_facts: list[str] = []