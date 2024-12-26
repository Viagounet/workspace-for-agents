from functools import cached_property
import os
from workspace_for_agents.llm_client import client


class EmailBox:
    def __init__(self) -> None:
        self.emails: list[Email] = []

    def display(self) -> str:
        if not self.emails:
            return "No emails yet!"
        email_box = "ID   | Turn | Sender                | Object\n"
        email_box += "-" * 50 + "\n"
        for email in self.emails:
            email_box += f"{str(email.id):4s} | {email.turn:4d} | {email.sender:20s} | {email.object}\n"
        return email_box

    def read_email(self, mail_id: int) -> str:
        requested_email = None
        for email in self.emails:
            if email.id == mail_id:
                requested_email = email
                break

        if not requested_email:
            return f"The email with id `{mail_id}` was not found."
        return requested_email.string


class Email:
    def __init__(
        self, sender: str, receiver: str, object: str, content: str, turn: int
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.object = object
        self._log = {}
        if "dynamic::" in content:
            messages = [
                {
                    "role": "developer",
                    "content": f"You are {self.sender} and must send a mail to {self.receiver} (object: {self.object}). You will receive some additional context clues from the user as well as instructions, you must follow the instructions very precisly, and use the context in a way that is smart. You will only answer with the content of the mail, not the object.",
                },
                {"role": "user", "content": content},
            ]
            self._log = messages
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=256,
            )
            content = completion.choices[0].message.content
        self.content = content
        self.turn = turn

    @cached_property
    def id(self):
        return int(str(hash(self))[-4:-1])

    @property
    def string(self):
        return f"OBJECT: {self.object}\nFROM: {self.sender}\nTO: {self.receiver}\nCONTENT: {self.content}"
