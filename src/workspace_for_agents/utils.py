import json
import os
import time
from typing import Callable, Optional
from pydantic import BaseModel, Field
from workspace_for_agents.llm_client import client


class ConditionVerification(BaseModel):
    argumentation: str = Field(
        description="A few sentences that explain why you think the condition is verified or not."
    )
    condition_is_verified: bool = Field(
        description="Wether or not the condition is verified."
    )


def semantic_is_true(condition: str, context: Optional[str | Callable] = None) -> bool:
    # Context can be a callable, in the case if it's set at initialization but can be dynamic
    if callable(context):
        context = context()

    additional_guidance = "According to your internal knowledge"
    if context:
        additional_guidance = "According to the provided context"
        context = f"<context>\n{context}\n</context>\n\n\n"
    instruction = f"{context}{additional_guidance}, would you say the following condition is valid?\n\nCONDITION = '{condition}'"
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": instruction,
            }
        ],
        response_format=ConditionVerification,
    )
    choice_taken_by_employee = completion.choices[0].message.parsed

    if choice_taken_by_employee:
        if os.environ["LOG_SEMANTIC"] == "True":
            with open(f"logs/{time.time()}.json", "w", encoding="utf-8") as f:
                json_log = choice_taken_by_employee.model_dump()
                json_log["prompt"] = instruction
                json.dump(json_log, f, ensure_ascii=False, indent=4)
        return choice_taken_by_employee.condition_is_verified

    print("Warning! choice_taken_by_employee is None.")
    return False
