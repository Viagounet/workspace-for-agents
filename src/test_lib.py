from argparse import ArgumentParser
from workspace_for_agents.tasks.send_mail_to_candidate import setup_task
from workspace_for_agents.environment import create_environnement_from_file
import os

parser = ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
args = parser.parse_args()

os.environ["VERBOSE_LOG"] = str(args.verbose)

env = create_environnement_from_file("src/envs/test_env_1.json")
task = setup_task(env)
print(env.get_employee_by_name("Ibrahim Mendoza").instructions)
env.run_task(task)
