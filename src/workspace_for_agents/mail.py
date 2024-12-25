from functools import cached_property
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
        if "dynamic::" in content:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "developer",
                        "content": f"Your role is to write a mail to {self.receiver} (note: you are {self.sender} according to the user's instruction. Note that the mail's object is already sent in the mail: '{self.object}'. You should only write the mail content. Do not invent anything that is not provided by the user.",
                    },
                    {"role": "user", "content": content},
                ],
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
