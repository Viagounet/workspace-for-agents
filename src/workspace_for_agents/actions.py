import ast
import os
import fitz

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from pathlib import Path

from workspace_for_agents.file_system import File, Folder, create_folder_structure
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

    @property
    @abstractmethod
    def json(self):
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

    @property
    def json(self):
        return {"mail_id": self.mail_id}


class CheckMailBox(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "check_mailbox() # Checks your mail box"

    def execute(self, env):
        env.agent.short_term_context += env.agent.email_box.display()

    @property
    def json(self):
        return {}


class SendEmail(Action):
    def __init__(
        self,
        receiver: str,
        object: str,
        content: str,
        attached_file: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.receiver = receiver
        self.object = object
        self.content = content
        self.dynamic_content: Optional[str] = None
        self.attached_file = attached_file

    @classmethod
    def description(self) -> str:
        return "send_mail_to(target_mail: str, object: str, content: str) # Sends an email to `target_mail`"

    def execute(self, env):
        if not self.source:
            raise RuntimeError("No source set for SendEmail")
        self.sender = self.source.email
        receiver_mail = self.receiver
        if "@company.com" in self.receiver:
            try:
                target_employee = env.get_employee_by_email(self.receiver)
                receiver_mail = target_employee.email
            except KeyError:
                self.source.short_term_context += (
                    f"<Info> {self.receiver} is not a valid email adress. </Info>"
                )
                return None

        email = Email(
            sender=self.source.email,
            receiver=receiver_mail,
            object=self.object,
            content=self.content,
            turn=env.current_turn,
            attached_file=self.attached_file,
        )
        if email._log != {} and os.environ["LOG_CALLS"] == "True":
            env.add_log(
                "dynamic_mail_debug",
                self.source.name,
                content=email._log,
            )
        if isinstance(self.content, Callable):
            self.dynamic_content = email.content
        if "@company.com" in self.receiver:
            target_employee.email_box.received_emails.append(email)

        self.source.email_box.sent_emails.append(email)
        if email.attached_file:
            path = Path(email.attached_file)
            if path.is_file():
                target_employee.folders.append()
            elif path.is_dir():
                folder = create_folder_structure(email.attached_file)
                target_employee.add_to_download_folder(folder)
            else:
                pass

    @property
    def json(self):
        output = {
            "sender": self.sender,
            "receiver": self.receiver,
            "object": self.object,
            "content": self.dynamic_content if self.dynamic_content else self.content,
            "attached_file": self.attached_file,
        }
        self.dynamic_content = None
        return output


class DisplayFiles(Action):
    def __init__(self):
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "display_files() # Displays all the available files at your disposal."

    def execute(self, env):
        if env.agent.folders == []:
            env.agent.short_term_context += "File system: you have no available files!"
        else:
            env.agent.short_term_context += env.agent.list_available_files()

    @property
    def json(self):
        return {}


def get_pdf_page_content_with_fitz(pdf_path, page_number):
    """
    Extracts and returns the content of a specified page from a PDF using PyMuPDF.

    :param pdf_path: Path to the PDF file.
    :param page_number: Page number to extract (1-based index).
    :return: Text content of the specified page or an error message.
    """
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        # Pages are zero-indexed in PyMuPDF, so subtract 1 from the page_number
        if 1 <= page_number <= len(pdf_document):
            page = pdf_document[page_number - 1]
            page_content = page.get_text()
            return page_content if page_content else "No text found on this page."
        else:
            return f"Invalid page number. The document has {len(pdf_document)} pages."
    except FileNotFoundError:
        return "The specified PDF file was not found."
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        # Ensure the document is closed after processing
        try:
            pdf_document.close()
        except NameError:
            pass


class ReadPDFPage(Action):
    def __init__(self, pdf_file_path: str, page: int):
        super().__init__()
        self.pdf_file_path = pdf_file_path
        self.page = page

    @classmethod
    def description(self) -> str:
        return "read_pdf_page(pdf_file_path: str, page_number: int) # Returns a string of the content of a PDF (note: pages enumeration start at 1)"

    def execute(self, env):
        path = self.markdown_path
        for agent_ref_path, absolute_path in env.agent.simlinks.items():
            path = path.replace(agent_ref_path, absolute_path)

        env.agent.short_term_context += get_pdf_page_content_with_fitz(path, self.page)

    @property
    def json(self):
        return {
            "pdf_file_path": self.pdf_file_path,
            "page": self.page,
        }


class ReadMarkdownFile(Action):
    def __init__(self, markdown_path: str):
        super().__init__()
        self.markdown_path = markdown_path

    @classmethod
    def description(self) -> str:
        return "read_markdown(markdown_path: str) # Returns a string of the content of a Markdown file"

    def execute(self, env):
        path = self.markdown_path
        for agent_ref_path, absolute_path in env.agent.simlinks.items():
            if absolute_path[-1] != "/":
                absolute_path = absolute_path + "/"
            path = path.replace(agent_ref_path, absolute_path)
        with open(path, "r", encoding="utf-8") as f:
            env.agent.short_term_context += f.read()

    @property
    def json(self):
        return {
            "markdown_path": self.markdown_path,
        }


class DisplayContacts(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "display_contacts() # Displays all the contacts stored in your adress"

    def execute(self, env):
        env.agent.short_term_context += env.agent.formated_contacts

    @property
    def json(self):
        return {}


class SetTaskAsCompleted(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "set_task_as_completed() # Will end the task, to call only when you think the objective is completed."

    def execute(self, env):
        pass

    @property
    def json(self):
        return {}


class Wait(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "wait() # Wait and does nothing"

    def execute(self, env):
        pass

    @property
    def json(self):
        return {}


class NoActionAfterParsing(Action):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def description(self) -> str:
        return "is taken when the parsing failed"

    def execute(self, env):
        pass

    @property
    def json(self):
        return {}


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
        "read_pdf_page": ReadPDFPage,
        "read_markdown": ReadMarkdownFile,
        "display_files": DisplayFiles,
        "set_task_as_completed": SetTaskAsCompleted,
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


class Condition:
    def __init__(
        self, condition: Callable[[], bool], name: Optional[str] = None
    ) -> None:
        self.condition = condition
        self.name = self.condition.__name__
        if name:
            self.name = name

    def is_true(self) -> bool:
        return self.condition()

    def _evaluate(self) -> dict[str, str | bool]:
        return {"name": self.name, "is_true": self.condition()}


class CompositeCondition(Condition):
    """
    Base class for composite conditions that combine multiple Condition objects.
    """

    def __init__(self, *conditions: Condition) -> None:
        # Instead of a single callable, store multiple Condition objects
        super().__init__(lambda: None)  # We won't use this lambda directly
        self.conditions = conditions

    def is_true(self) -> bool:
        # Subclasses (AND/OR) must implement their own logic.
        raise NotImplementedError

    def _evaluate(self) -> dict[str, Any]:
        conditions_values = []
        for condition in self.conditions:
            conditions_values.append(condition._evaluate())
        return {"condition_type": "composite_generic", "details": conditions_values}


class AndCondition(CompositeCondition):
    def is_true(self) -> bool:
        return all(condition.is_true() for condition in self.conditions)

    def _evaluate(self) -> dict[str, Any]:
        conditions_values = []
        for condition in self.conditions:
            conditions_values.append(condition._evaluate())
        return {"condition_type": "and_condition", "details": conditions_values}


class OrCondition(CompositeCondition):
    def is_true(self) -> bool:
        return any(condition.is_true() for condition in self.conditions)

    def _evaluate(self) -> dict[str, Any]:
        conditions_values = []
        for condition in self.conditions:
            conditions_values.append(condition._evaluate())
        return {"condition_type": "or_condition", "details": conditions_values}


@dataclass
class ConditionedAction:
    condition: Condition | Callable
    linked_action: Action
    score: int
    requires_completion: list = field(default_factory=list)
    is_completed: bool = False
    stays_after_completion: bool = False

    def __post_init__(self):
        if isinstance(self.condition, Callable):
            self.condition = Condition(self.condition)

    def add_requirement(self, requirement):
        self.requires_completion.append(requirement)

    def complete_requirement(self, requirement):
        if requirement in self.requires_completion:
            self.requires_completion.remove(requirement)
