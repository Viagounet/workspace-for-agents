from workspace_for_agents.tasks.send_mail_to_candidate import setup_task
from workspace_for_agents.environment import create_environnement_from_file


env = create_environnement_from_file("src/envs/test_env_1.json")
task = setup_task(env)
env.run_task(task)
