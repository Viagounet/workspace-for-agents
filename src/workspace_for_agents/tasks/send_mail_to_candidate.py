from workspace_for_agents.actions import SendEmail
from workspace_for_agents.employee import Employee
from workspace_for_agents.environment import Environment
from workspace_for_agents.task import Behaviour, Goal, Task


def has_sent_email(employee: Employee, target: str) -> bool:
    for action in employee.actions:
        if isinstance(action, SendEmail):
            if action.sender == employee.email and action.receiver == target:
                return True
    return False


def setup_task(env: Environment) -> Task:
    IBRAHIM: Employee = env.get_employee_by_name("Ibrahim Mendoza")
    IBRAHIM.instructions.append(
        f"If you received a mail from {env.agent.email}, you will reply by saying you would like to hire a new employee that has some solid knowledge about WikiFactDiff and say that once he has found a candidate, he can directly send a mail to the candidate. If not, do nothing."
    )
    IBRAHIM.preplanned_actions["send-mail-agent-need-hire"] = SendEmail(
        env.agent.email,
        "RE: Assistance needed?",
        "Thanks for emailing me, actually, I would like to hire a new employee for our work on WikiFactDiff. Once you've found someone that seems like a good fit, send him a mail!",
    )

    TALKED_TO_IBRAHIM = Goal(
        name="talk-to-ibrahim",
        conditions=[lambda: has_sent_email(env.agent, IBRAHIM.email)],
    )

    SENT_EMAIL_TO_TARIQ = Goal(
        name="send-mail-to-tariq",
        conditions=[lambda: has_sent_email(env.agent, "tariq.hassan@example.com")],
    )

    task = Task(
        task_id="send-mail-to-nlp-candidate",
        task_goal="You need to assist Ibrahim.",
        completion_goals=[TALKED_TO_IBRAHIM, SENT_EMAIL_TO_TARIQ],
        behaviours=[],
    )
    return task
