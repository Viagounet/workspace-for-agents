from workspace_for_agents.environment import create_environnement_from_file


env = create_environnement_from_file("src/envs/test_env_1.json")
first_employee = env.employees[2]
first_employee.list_available_files()