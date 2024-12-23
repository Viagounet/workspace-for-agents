from abc import ABC, abstractmethod
from typing import Optional


class Action(ABC):
    def __init__(self) -> None:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self) -> str:
        pass


class SendEmail(Action):
    def __init__(self, receiver: str, content: str) -> None:
        super().__init__()
        self.receiver = receiver
        self.content = content

    @classmethod
    def description(self) -> str:
        return "send_mail_to(target_mail: str, content: str) # Sends an email to `target_mail`"

    def execute(self):
        print(f"Sending an email to: {self.receiver}")
        pass


class Wait(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "wait() # Wait and does nothing"

    def execute(self):
        pass


class NoActionAfterParsing(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "is taken when the parsing failed"

    def execute(self):
        pass


def parse_action(action_str: str) -> Optional[Action]:
    """Parse a string command into an Action object.

    Args:
        action_str: String command to parse (e.g. "send_mail_to(bob@example.com, Hello)")

    Returns:
        Action object if valid command, None if invalid
    """
    action_str = action_str.strip()

    action_name = action_str[: action_str.find("(")]
    args_str = action_str[action_str.find("(") + 1 : action_str.find(")")]
    args = [arg.strip().strip("\"'") for arg in args_str.split(",")] if args_str else []
    # Map action names to their corresponding classes and required arguments
    action_map = {
        "wait": (Wait, []),
        "send_mail_to": (SendEmail, ["agent@company.com", "target_mail", "content"]),
    }

    if action_name in action_map:
        action_class, default_args = action_map[action_name]
        # For actions with no arguments
        if not default_args:
            return action_class()
        return action_class(*args)
    return NoActionAfterParsing()
