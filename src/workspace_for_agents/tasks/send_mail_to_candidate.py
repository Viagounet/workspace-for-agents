from workspace_for_agents.actions import SendEmail
from workspace_for_agents.employee import Employee
from workspace_for_agents.environment import Environment
from workspace_for_agents.task import Goal, Task


def has_sent_email(employee: Employee, target: str) -> bool:
    for action in employee.actions:
        if isinstance(action, SendEmail):
            if action.sender == employee.mail and action.receiver == target:
                return True
    return False


def setup_task(env: Environment) -> Task:
    TALKED_TO_IBRAHIM = Goal(
        name="talk-to-ibrahim",
        conditions=[has_sent_email(env.agent, "ibrahim.mendoza@company.com")],
    )
    SENT_EMAIL_TO_TARIQ = Goal(
        name="send-mail-to-tariq",
        conditions=[has_sent_email(env.agent, "tariq.hassan@example.com")],
    )

    task = Task(
        task_id="send-mail-to-nlp-candidate",
        task_goal="You need to assist Ibrahim.",
        completion_goals=[TALKED_TO_IBRAHIM, SENT_EMAIL_TO_TARIQ],
        behaviours=[],
    )
    return task
