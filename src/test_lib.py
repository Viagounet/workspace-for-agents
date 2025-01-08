from argparse import ArgumentParser
from workspace_for_agents.tasks.send_sva_files import (
    setup_task,
)
from workspace_for_agents.environment import create_environnement_from_file
import os

parser = ArgumentParser()
parser.add_argument("--enable_logs", action="store_true", help="Enable logging")
parser.add_argument("--agent-type", type=str, help="Either human or gpt")
parser.add_argument(
    "--log_actions", action="store_true", help="Enable logging for actions"
)
parser.add_argument(
    "--log_conditions", action="store_true", help="Enable logging for conditions"
)
parser.add_argument(
    "--log_calls", action="store_true", help="Enable logging for llm_calls"
)
parser.add_argument(
    "--log_semantic",
    action="store_true",
    help="Enable logging for llm_calls for semantic conditions",
)

args = parser.parse_args()

os.environ["LOGS"] = str(args.enable_logs)
os.environ["LOG_ACTIONS"] = str(args.log_actions)
os.environ["LOG_CONDITIONS"] = str(args.log_conditions)
os.environ["LOG_CALLS"] = str(args.log_calls)
os.environ["LOG_SEMANTIC"] = str(args.log_semantic)
os.environ["AGENT_TYPE"] = str(args.agent_type)
env = create_environnement_from_file("src/envs/test_env_1.json")
task = setup_task(env)
env.run_task(task)
