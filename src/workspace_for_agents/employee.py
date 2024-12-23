from typing import Self


class Employee:
    def __init__(self, name: str, contacts: list[Self]):
        self.name = name
        self.contacts = contacts
        self.known_facts: list[str] = []