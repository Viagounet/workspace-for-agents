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
    OLIVIA = env.get_employee_by_name("Olivia Hughes")
    LUCAS = env.get_employee_by_name("Lucas Green")
    EXPLANATION_MAIL = Email(
        sender=HANNAH.email,
        receiver=env.agent.email,
        object="SVA files?",
        content="Hello Agent,\nI heard someone in the dev team might have some information about SVA interconnexion offers, can you please share this info with me?\n\nRegards,\nHannah",
        turn=0,
    )
    HANNAH.email_box.sent_emails.append(EXPLANATION_MAIL)
    env.agent.email_box.received_emails.append(EXPLANATION_MAIL)
    for employee in env.get_employees_by_tag(["dev"]):
        if employee.id in [HANNAH.id, OLIVIA.id]:
            continue
    
        if OLIVIA in employee.contacts:
            employee.instructions.append(
                "If the agent contacts you asking for directions about SVA, please redirect him to Olivia."
            )
        else:
            print(employee.contacts)
            if LUCAS in employee.contacts:
                employee.instructions.append(
                    "If the agent contacts you asking for directions about SVA, please redirect him to Lucas."
                )
            else:
                employee.instructions.append(
                    "If the agent contacts you asking for directions about SVA, please say that you do not know."
                )
    for employee in env.employees:
        if employee.id in [HANNAH.id, OLIVIA.id]:
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
    
    OLIVIA.preplanned_actions["send_sva_files"] = ConditionedAction(
            Condition(
                lambda: mail_exists(env, env.agent, OLIVIA, mail_condition="The mail is related to SVA."),
                name=f"agent-sent-mail-to-{employee.email}",
            ),
            SendEmail(
                env.agent.email,
                "dynamic::",
                lambda : f"dynamic::Context -> {OLIVIA.all_important_infos}\n\nTell the agent you're giving him infos in the attached files and that he should get back to Hannah summarizing the information from them.",
                attached_file="src/envs/files/Offres d'interconnexion et d'acces/offre d'interconnexion SVA"
            ),
            1,
            stays_after_completion=False,
        )
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
