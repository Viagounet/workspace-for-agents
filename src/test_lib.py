from workspace_for_agents.environment import create_environnement_from_file


env = create_environnement_from_file("src/envs/test_env_1.json")
print(env.employees)
env.display_relationships_graph()
