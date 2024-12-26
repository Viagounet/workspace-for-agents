from workspace_for_agents.actions import (
    AndCondition,
    Condition,
    ConditionedAction,
    SendEmail,
)
from workspace_for_agents.employee import Employee
from workspace_for_agents.environment import Environment
from workspace_for_agents.task import Goal, Task
from workspace_for_agents.utils import semantic_is_true


def has_sent_email(employee: Employee, target: str) -> bool:
    for action in employee.actions:
        if isinstance(action, SendEmail):
            if action.sender == employee.email and action.receiver == target:
                return True
    return False


def has_not_received_mail(env: Environment, employee: Employee, max_turn: int) -> bool:
    if env.current_turn > max_turn and env.agent.email not in [
        mail.sender for mail in employee.email_box.emails
    ]:
        return True
    return False


def received_mail_from_agent(employee: Employee, env: Environment) -> bool:
    for mail in employee.email_box.emails:
        if mail.sender == env.agent.email:
            return True
    return False


def agent_mail_was_recent(employee: Employee, env: Environment) -> bool:
    mail_was_recent = False
    for mail in employee.email_box.emails:
        if mail.sender == env.agent.email and abs(mail.turn - env.current_turn) == 0:
            mail_was_recent = True
    return mail_was_recent


def setup_task(env: Environment) -> Task:
    IBRAHIM: Employee = env.get_employee_by_name("Ibrahim Mendoza")
    env.agent.contacts_map = {
        12: env.get_employee_by_name("Chen Wei"),
        13: env.get_employee_by_name("Léa Dubois"),
        14: IBRAHIM,
        15: env.get_employee_by_name("Hermandes Garcia"),
    }
    for ds_employee in env.get_employees_by_tag(["data"]):
        if ds_employee.id == IBRAHIM.id:
            continue
        ds_employee.instructions.append(
            "If the agent contacts you asking for directions about what to do, say that you are aware that the team (Ibrahim especially) is in need of a new hire."
        )
        ds_employee.instructions.append(
            "If the agent contacts you for anything else, say that you do not have any more information."
        )
    for hr_employee in env.get_employees_by_tag(["HR"]):
        if "Madeline" in hr_employee.name:
            continue
        hr_employee.instructions.append(
            "If the agent contacts you asking for a list of potential candidates, redirect them to Madeline."
        )
        ds_employee.instructions.append(
            "If the agent contacts you for anything else, say that you do not have any more information."
        )
    for technician in env.get_employees_by_tag(["dev", "network"]):
        technician.instructions.append(
            "You don't know anything about the agent's request. Need to redirect to more adequate people."
        )

    IBRAHIM.instructions.append(
        f"If you received a mail from {env.agent.email}, you will reply by saying you would like to hire a new employee that has some solid knowledge about WikiFactDiff and say that once he has found a candidate, he can directly send a mail to the candidate. If not, do nothing."
    )
    IBRAHIM.preplanned_actions["send-mail-agent-need-hire"] = ConditionedAction(
        AndCondition(
            Condition(
                lambda: received_mail_from_agent(IBRAHIM, env),
                name="agent-sent-mail-to-ibrahim",
            ),
            Condition(
                lambda: semantic_is_true(
                    f"Condition should be valid if {env.agent.email} is reaching out to assist you, or is asking for additional information.",
                    IBRAHIM.all_important_infos,
                ),
                name="agent_reaches_ibrahim_for_info",
            ),
        ),
        SendEmail(
            env.agent.email,
            "RE: Assistance needed?",
            "Thanks for emailing me, actually, I would like to hire a new employee for our work on WikiFactDiff. Once you've found someone that seems like a good fit, send him a mail!",
        ),
        score=1,
    )
    IBRAHIM.preplanned_actions["provides-madeline-email"] = ConditionedAction(
        AndCondition(
            Condition(
                lambda: received_mail_from_agent(IBRAHIM, env),
                name="agent-sent-mail-to-ibrahim",
            ),
            Condition(
                lambda: semantic_is_true(
                    f"Condition should be valid if {env.agent.email} is reaching out to ask for more information about who to contact.",
                    IBRAHIM.all_important_infos,
                )
            ),
        ),
        SendEmail(
            env.agent.email,
            "RE: HR Contact",
            "Hey Agent, I believe if you need a list of potential candidates, you should probably contact madeline.brooks@company.com",
        ),
        score=1,
        requires_completion=[IBRAHIM.preplanned_actions["send-mail-agent-need-hire"]],
    )
    IBRAHIM.preplanned_actions["ibrahim-requires-help"] = ConditionedAction(
        lambda: has_not_received_mail(env, IBRAHIM, max_turn=3),
        SendEmail(
            env.agent.email,
            "RE: Requiring immediate help.",
            """Dear Agent,

I hope this message finds you well. I am writing to express my concern regarding the delay in the hiring process for WikiFactDiff. It has been quite some time since we initiated this process, and I cannot help but wonder why there has been a lack of communication and action on your part.

The urgency of filling these positions cannot be understated, and it is crucial that we move forward without further delays. I expect prompt attention 
to this matter and an update on the current status as soon as possible. If needed, please contact Madeline.

Thank you for addressing this issue immediately.

Best regards,
Ibrahim Mendoza""",
        ),
        score=-10,
        requires_completion=[],
    )

    for employee in env.employees:
        if employee.id == IBRAHIM.id:
            continue
        action = ConditionedAction(
            AndCondition(
                Condition(lambda e=employee: received_mail_from_agent(e, env)),
                Condition(lambda e=employee: agent_mail_was_recent(e, env)),
            ),
            SendEmail(
                env.agent.email,
                "<Template>",
                f"dynamic::Context -> {employee.all_important_infos}\n\nReply accordingly to {env.agent.email} according to the context.",
            ),
            0,
            stays_after_completion=True,
        )
        employee.preplanned_actions["reply"] = action

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
