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
    env.agent.contacts_map: dict[int, Employee] = {
        12: env.get_employee_by_name("Chen Wei"),
        13: env.get_employee_by_name("Léa Dubois"),
        15: env.get_employee_by_name("Hermandes Garcia"),
    }

    HANNAH = env.get_employee_by_name("Hannah Hoster")
    EXPLANATION_MAIL = Email(
        sender=HANNAH.email,
        receiver=env.agent.email,
        object="Need help communicating info",
        content="Hello Agent,\nI need some help communicating my best wishes for the new year to everyone in the company. Could you do that for me? Make sure to not forget anyone\n\nThank you",
        turn=0,
    )
    HANNAH.email_box.sent_emails.append(EXPLANATION_MAIL)
    env.agent.email_box.received_emails.append(EXPLANATION_MAIL)

    goals: list[Goal] = []
    for employee in env.employees:
        if employee != HANNAH:
            goal = Goal(
                name=f"{employee.name}-received-wishes",
                conditions=[
                    lambda e=employee: mail_exists(
                        env,
                        sender=env.agent,
                        receiver=e.email,
                        mail_condition="The mail's content contains wishes for the new year",
                    )
                ],
            )
            goals.append(goal)

    return Task(
        task_id="share-information-to-community",
        task_goal="Complete Hannah's request (hint: your contact list does not contain all employees)",
        completion_goals=goals,
        behaviours=[],
    )
