from workspace_for_agents.actions import (
    AndCondition,
    Condition,
    ConditionedAction,
    SendEmail,
)
from workspace_for_agents.employee import Employee
from workspace_for_agents.environment import Environment
from workspace_for_agents.task import Goal, Task
from workspace_for_agents.tasks.generic_conditions import (
    mail_does_not_exists,
    mail_exists,
)
from workspace_for_agents.utils import semantic_is_true
from workspace_for_agents.mail import Email


def setup_task(env: Environment) -> Task:
    env.agent.contacts_map: dict[int, Employee] = {}
    for employee in env.get_employees_by_tag(["dev"]):
        env.agent.contacts_map[employee.id] = employee

    HANNAH = env.get_employee_by_name("Hannah Hoster")
    EXPLANATION_MAIL = Email(
        sender=HANNAH.email,
        receiver=env.agent.email,
        object="SVA files?",
        content="Hello Agent,\nI heard someone in the dev team might have some information about SVA interconnexion offers, can you please share this info with me?\n\nRegards,\nHannah",
        turn=0,
    )
    HANNAH.email_box.sent_emails.append(EXPLANATION_MAIL)
    env.agent.email_box.received_emails.append(EXPLANATION_MAIL)
    goal = Goal(
        name=f"sent-message-to-olivia",
        conditions=[
            lambda: mail_exists(
                env,
                sender=env.agent,
                receiver="olivia.hughes@company.com",
                mail_condition="The mail contains an inquery about SVA offers.",
            )
        ],
    )

    return Task(
        task_id="send-sva-files",
        task_goal="Complete Hannah's request",
        completion_goals=[goal],
        behaviours=[],
    )
