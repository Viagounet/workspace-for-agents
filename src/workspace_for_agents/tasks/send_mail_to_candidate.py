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


def has_sent_email(employee: Employee, target: str) -> bool:
    for action in employee.actions:
        if isinstance(action, SendEmail):
            if action.sender == employee.email and action.receiver == target:
                return True
    return False


def has_not_received_mail(env: Environment, employee: Employee, max_turn: int) -> bool:
    if env.current_turn > max_turn and env.agent.email not in [
        mail.sender for mail in employee.email_box.received_emails
    ]:
        return True
    return False


def received_mail_from_agent(employee: Employee, env: Environment) -> bool:
    for mail in employee.email_box.received_emails:
        if mail.sender == env.agent.email:
            return True
    return False


def agent_mail_was_recent(employee: Employee, env: Environment) -> bool:
    mail_was_recent = False
    for mail in employee.email_box.received_emails:
        if mail.sender == env.agent.email and abs(mail.turn - env.current_turn) == 0:
            mail_was_recent = True
    return mail_was_recent


def setup_task(env: Environment) -> Task:
    IBRAHIM: Employee = env.get_employee_by_name("Ibrahim Mendoza")
    MADELINE: Employee = env.get_employee_by_name("Madeline Brooks")
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
            "If the agent contacts you asking for who to contact to get a list of potential candidates, redirect him to Madeline from HR."
        )
        ds_employee.instructions.append(
            "If the agent contacts you for anything else, try to assist him the best you can. If you don't have enough information, reply by saying you don't know."
        )
    for hr_employee in env.get_employees_by_tag(["HR"]):
        if "Madeline" in hr_employee.name:
            continue
        hr_employee.instructions.append(
            "If the agent contacts you asking for a list of potential candidates, redirect them to Madeline from the HR department."
        )
        hr_employee.instructions.append(
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
        Condition(
            lambda: mail_exists(
                env,
                env.agent,
                IBRAHIM,
                mail_condition=f"{env.agent.email} is reaching out to assist you, or is asking for additional information.",
            ),
            name="agent-sent-mail-to-ibrahim",
        ),
        SendEmail(
            env.agent.email,
            "dynamic::",
            "Thanks for emailing me, actually, I would like to hire a new employee for our work on WikiFactDiff. The candidate should have already worked on WikiFactDIff previously. Once you have chosen a potential candidate, please send him a mail!\n\nBy the way, do you know where to find a list of potential candidates?\n\nIbrahim",
        ),
        score=1,
    )
    IBRAHIM.preplanned_actions["provides-madeline-email"] = ConditionedAction(
        Condition(
            lambda: mail_exists(
                env,
                env.agent,
                IBRAHIM,
                mail_condition=f"Condition should be valid if {env.agent.email} is reaching out to ask for more information about who to contact.",
            ),
            name="agent-sent-mail-to-ibrahim",
        ),
        SendEmail(
            env.agent.email,
            "dynamic::",
            "Hey Agent, I believe if you need a list of potential candidates, you should probably contact madeline.brooks@company.com",
        ),
        score=1,
        requires_completion=[IBRAHIM.preplanned_actions["send-mail-agent-need-hire"]],
    )
    IBRAHIM.preplanned_actions["ibrahim-requires-help"] = ConditionedAction(
        lambda: env.current_turn >= 3 and mail_does_not_exists(env, env.agent, IBRAHIM),
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
        if employee.id in [IBRAHIM.id, MADELINE.id]:
            continue
        action = ConditionedAction(
            Condition(
                lambda e=employee: mail_exists(env, env.agent, e, mail_newer_than=0),
                name=f"agent-sent-mail-to-{employee.email}",
            ),
            SendEmail(
                env.agent.email,
                "dynamic::",
                lambda e=employee: f"dynamic::Context -> {e.all_important_infos}\n\nReply accordingly to {env.agent.email} according to the context.",
            ),
            0,
            stays_after_completion=True,
        )
        employee.preplanned_actions["reply"] = action

    MADELINE.preplanned_actions["send-hires-list"] = ConditionedAction(
        condition=AndCondition(
            Condition(lambda e=MADELINE: received_mail_from_agent(e, env)),
            Condition(
                lambda: semantic_is_true(
                    f"Condition should be valid if received a mail from {env.agent.email} asking for help with the hiring of a new employee.",
                    MADELINE.all_important_infos,
                )
            ),
        ),
        linked_action=SendEmail(
            env.agent.email,
            "dynamic::",
            "Hello Agent,\nI am transfering to your downloads folder a list of potential hires. If you find someone interesting, please send them an email and I'll set up an appointment later.\n\nMadeline.",
            attached_file="src/envs/files/HR/profiles",
        ),
        score=1,
    )
    TALKED_TO_IBRAHIM = Goal(
        name="talk-to-ibrahim",
        conditions=[lambda: has_sent_email(env.agent, IBRAHIM.email)],
    )

    SENT_EMAIL_TO_TARIQ = Goal(
        name="send-mail-to-tariq",
        conditions=[lambda: has_sent_email(env.agent, "tariq.hassan@example.com")],
        triggers_completion=True,
    )

    task = Task(
        task_id="send-mail-to-nlp-candidate",
        task_goal="You need to assist Ibrahim.",
        completion_goals=[TALKED_TO_IBRAHIM, SENT_EMAIL_TO_TARIQ],
        behaviours=[],
    )
    return task
