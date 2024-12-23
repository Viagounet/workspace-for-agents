from functools import cached_property


class EmailBox:
    def __init__(self) -> None:
        self.emails = []

    def __str__(self) -> str:
        email_box = "ID   | Turn | Sender                | Object\n"
        email_box += "-" * 50 + "\n"
        for email in self.emails:
            email_box += f"{email.id:4s} | {email.turn:4d} | {email.sender:20s} | {email.object}\n"
        return email_box


class Email:
    def __init__(
        self, sender: str, receiver: str, object: str, content: str, turn: int
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.object = object
        self.content = content
        self.turn = turn

    @cached_property
    def id(self):
        return str(hash(self))[-4:-1]
