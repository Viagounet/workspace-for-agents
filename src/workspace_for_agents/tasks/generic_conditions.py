from typing import Optional
from workspace_for_agents.employee import Employee
from workspace_for_agents.environment import Environment
from workspace_for_agents.utils import semantic_is_true


def mail_exists(
    environment: Environment,
    sender: Employee,
    receiver: str | Employee,
    mail_condition: Optional[str] = None,
    mail_older_than: Optional[int] = None,
    mail_newer_than: Optional[int] = None,
) -> bool:
    if isinstance(receiver, Employee):
        receiver = receiver.email
    for sent_mail in sender.email_box.sent_emails:
        if (
            mail_older_than != None
            and environment.current_turn - sent_mail.turn < mail_older_than
        ):
            continue
        if (
            mail_newer_than != None
            and environment.current_turn - sent_mail.turn > mail_newer_than
        ):
            continue
        if receiver == sent_mail.receiver:
            if not mail_condition:
                return True
            if semantic_is_true(
                f"You should set the condition as true if the following proposition is true: {mail_condition}''",
                sent_mail.string,
            ):
                return True
    return False


def mail_does_not_exists(
    environment: Environment,
    sender: Employee,
    receiver: str | Employee,
    mail_condition: Optional[str] = None,
    max_delta_turns: Optional[int] = None,
) -> bool:
    return not mail_exists(
        environment, sender, receiver, mail_condition, max_delta_turns
    )
