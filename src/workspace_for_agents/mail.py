from functools import cached_property
from typing import Callable, Optional
from workspace_for_agents.llm_client import client


class EmailBox:
    def __init__(self) -> None:
        self.received_emails: list[Email] = []
        self.sent_emails: list[Email] = []

    def display(self) -> str:
        if not self.received_emails:
            return "No emails yet!"
        email_box = "ID   | Turn | Sender                | Object\n"
        email_box += "-" * 50 + "\n"
        for email in self.received_emails:
            email_box += f"{str(email.id):4s} | {email.turn:4d} | {email.sender:20s} | {email.object}\n"
        return email_box

    def read_email(self, mail_id: int) -> str:
        requested_email = None
        for email in self.received_emails:
            if email.id == mail_id:
                requested_email = email
                break

        if not requested_email:
            return f"The email with id `{mail_id}` was not found."
        return requested_email.string

    def display_all_in_chronological_order(self) -> str:
        """
        Returns a string with all the mails (both received and sent) in
        chronological order (based on their 'turn' attribute). If two or
        more emails have the same turn, the received mail(s) appear
        before the sent mail(s). This method uses the Email.string
        property to include the full content of each email.
        """

        # Combine emails along with a marker for type ('received' or 'sent')
        all_emails_tagged = [(email, "received") for email in self.received_emails] + [
            (email, "sent") for email in self.sent_emails
        ]

        if not all_emails_tagged:
            return "No emails yet!"

        # Sort primarily by 'turn' ascending, secondarily by type:
        #   'received' (0) should come before 'sent' (1) if turn is the same
        def sort_key(item):
            email, mail_type = item
            return (email.turn, 0 if mail_type == "received" else 1)

        all_emails_sorted = sorted(all_emails_tagged, key=sort_key)

        # Build the output string using the email.string method
        output = []
        for email, mail_type in all_emails_sorted:
            output.append(email.string)

        # Join the email representations with a blank line in between
        return "\n\n".join(output)


class Email:
    def __init__(
        self,
        sender: str,
        receiver: str,
        object: str,
        content: str,
        turn: int,
        attached_file: Optional[str] = None,
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.object = object
        self.attached_file: str = attached_file
        self._log = {}

        if isinstance(content, Callable):
            content = content()

        if "dynamic::" in content:
            content = content.split("dynamic::")[1]
            messages = [
                {
                    "role": "developer",
                    "content": f"You are {self.sender} and must send a mail to {self.receiver}. You will receive some additional context clues from the user as well as instructions, you must follow the instructions very precisly, and use the context in a way that is smart. You will only answer with the content of the mail, not the object.",
                },
                {"role": "user", "content": content},
            ]
            self._log["dynamic_message"] = messages
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=256,
            )
            content = completion.choices[0].message.content

        if self.object == "dynamic::":
            messages = [
                {
                    "role": "developer",
                    "content": f"You are {self.sender} and must send a mail to {self.receiver}. Your role is to create a mail object for the user mail.",
                },
                {
                    "role": "user",
                    "content": f"Mail: {content}\n\n===\nCan you think of a short mail object? Answer only with the object.",
                },
            ]
            self._log["dynamic_object"] = messages
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=10,
            )
            self.object = completion.choices[0].message.content
        self.content = content
        self.turn = turn

    @cached_property
    def id(self):
        return int(str(hash(self))[-4:-1])

    @property
    def string(self):
        return f"OBJECT: {self.object}\nFROM: {self.sender}\nTO: {self.receiver}\nCONTENT: {self.content}"
