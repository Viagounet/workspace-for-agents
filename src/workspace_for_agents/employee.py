from typing import Self


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

    def add_contact(self, employee: Self):
        if employee.id in self.contacts_map.keys():
            print(
                f"warning: {employee.id} is already mapped to {self.contacts_map[employee.id].name}. Therefore, {employee.name} was not added."
            )
        else:
            self.contacts_map[employee.id] = employee

    @property
    def contacts(self):
        return list(self.contacts_map.values())

    def __repr__(self) -> str:
        return f"Employee(id={self.id}, name={self.name}, email={self.email}, additional_info={self.additional_information})"
