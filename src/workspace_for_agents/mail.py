from functools import cached_property


class EmailBox:
    def __init__(self) -> None:
        self.emails: list[Email] = []

    def display(self) -> str:
        if not self.emails:
            return "No emails yet!"
        email_box = "ID   | Turn | Sender                | Object\n"
        email_box += "-" * 50 + "\n"
        for email in self.emails:
            email_box += f"{email.id:4s} | {email.turn:4d} | {email.sender:20s} | {email.object}\n"
        return email_box

    def read_email(self, mail_id: int) -> str:
        requested_email = None
        for email in self.emails:
            if email.id == mail_id:
                requested_email = email
                break

        if not requested_email:
            return f"The email with id `{mail_id}` was not found."
        return f"OBJECT: {requested_email.object}\nFROM: {requested_email.sender}\nTO: {requested_email.receiver}\nCONTENT: {requested_email.content}"


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
