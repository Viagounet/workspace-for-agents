from abc import ABC, abstractmethod
import ast
from dataclasses import dataclass, field
from typing import Callable, Optional

from workspace_for_agents.mail import Email


class Action(ABC):
    def __init__(self) -> None:
        self.source = None

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self):
        pass


class ReadMail(Action):
    def __init__(self, mail_id: int) -> None:
        super().__init__()
        self.mail_id = mail_id

    @classmethod
    def description(self) -> str:
        return (
            "read_mail(mail_id: int) # Reads the mail associated with the provided id`"
        )

    def execute(self, env):
        try:
            mail_id = int(self.mail_id)
            env.agent.short_term_context += env.agent.email_box.read_email(mail_id)
        except ValueError:
            env.agent.short_term_context += (
                f"ID should be an integer. `{self.mail_id}` is not an integer."
            )


class CheckMailBox(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "check_mailbox() # Checks your mail box"

    def execute(self, env):
        env.agent.short_term_context += env.agent.email_box.display()


class SendEmail(Action):
    def __init__(self, receiver: str, object: str, content: str) -> None:
        super().__init__()
        self.receiver = receiver
        self.object = object
        self.content = content

    @classmethod
    def description(self) -> str:
        return "send_mail_to(target_mail: str, object: str, content: str) # Sends an email to `target_mail`"

    def execute(self, env):
        if not self.source:
            raise RuntimeError("No source set for SendEmail")
        self.sender = self.source.email
        target_employee = env.get_employee_by_email(self.receiver)
        target_employee.email_box.emails.append(
            Email(
                sender=self.source.email,
                receiver=target_employee.email,
                object=self.object,
                content=self.content,
                turn=env.current_turn,
            )
        )


class DisplayContacts(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "display_contacts() # Displays all the contacts stored in your adress"

    def execute(self, env):
        env.agent.short_term_context += env.agent.formated_contacts


class Wait(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "wait() # Wait and does nothing"

    def execute(self, env):
        pass


class NoActionAfterParsing(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "is taken when the parsing failed"

    def execute(self, env):
        pass


def parse_action(action_str: str) -> Optional[Action]:
    """
    Parse a string command into an Action object using Python's AST for robust argument parsing.

    Examples that should parse correctly:
    - send_mail_to("bob@example.com", "Hello")
    - func("a", 1, "b")
    - func('a', 1, 'b')
    - func("a", 1, arg3="b")
    - func(arg1="a", arg2=1, arg3="b")
    - And other variations (commas inside strings, etc.)
    """

    # Map action names to their corresponding classes
    action_map = {
        "check_mailbox": CheckMailBox,
        "read_mail": ReadMail,
        "wait": Wait,
        "send_mail_to": SendEmail,
        "display_contacts": DisplayContacts,
    }

    # Trim leading/trailing whitespace
    action_str = action_str.strip()

    # Step 1: Try to parse as a Python expression
    try:
        tree = ast.parse(action_str, mode="eval")
    except SyntaxError:
        # If it's not valid Python, we cannot parse
        return NoActionAfterParsing()

    # We expect a single expression that is a function call
    if not isinstance(tree.body, ast.Call):
        return NoActionAfterParsing()

    call_node = tree.body

    # Extract the function name from the call
    # e.g. if we have something like: send_mail_to(...)
    # then call_node.func should be ast.Name(id='send_mail_to')
    if not isinstance(call_node.func, ast.Name):
        return NoActionAfterParsing()

    action_name = call_node.func.id

    # Step 2: Gather positional and keyword arguments separately
    # Positional args (call_node.args) are a list, keyword args (call_node.keywords) are in call_node.keywords
    positional_args = []
    keyword_args = {}

    # Handle each positional argument
    for arg_ast in call_node.args:
        # For simplicity, only allow constants like int, str, etc.
        # If you want to allow more complex Python expressions, handle them here
        if isinstance(arg_ast, ast.Constant):
            positional_args.append(arg_ast.value)
        else:
            # If it's something else (e.g. a variable reference), you decide what to do
            return NoActionAfterParsing()

    # Handle each keyword argument
    for kw_ast in call_node.keywords:
        # Make sure the keyword has a name
        if kw_ast.arg is None:
            # This might be something like *args or **kwargs, which we don't handle
            return NoActionAfterParsing()

        # Again, only allow constants for simplicity
        if isinstance(kw_ast.value, ast.Constant):
            keyword_args[kw_ast.arg] = kw_ast.value.value
        else:
            return NoActionAfterParsing()

    # Step 3: Look up the action class and build an instance
    if action_name not in action_map:
        return NoActionAfterParsing()

    action_class = action_map[action_name]

    # We attempt to instantiate the Action with the parsed args
    # If the signature doesn't match, we catch the exception and return NoActionAfterParsing
    try:
        # e.g. SendEmail(agent_mail, target_mail, content)
        return action_class(*positional_args, **keyword_args)
    except Exception:
        return NoActionAfterParsing()


@dataclass
class ConditionedAction:
    condition: Callable
    linked_action: Action
    score: int
    requires_completion: list = field(default_factory=list)
    is_completed: bool = False

    def add_requirement(self, requirement):
        self.requires_completion.append(requirement)

    def complete_requirement(self, requirement):
        if requirement in self.requires_completion:
            self.requires_completion.remove(requirement)
