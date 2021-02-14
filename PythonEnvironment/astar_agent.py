"""
astar_agent.py
Purpose: implements an agent that moves optimally in the level
Author: Michael Probst
"""
import random
import util
from scavenger_env import ScavengerEnv

MOVES = ['U', 'D', 'L', 'R']

class AstarAgent():
    def __init__(self, start_score, env):
        self.reward = start_score
        self.sequence = self.a_star_search(env, self.null_heuristic)
        self.move_count = 0

    def suggest_move(self, env):
        #seq = self.a_star_search(env)
        move = self.sequence[self.move_count]
        self.move_count += 1
        return move

    def null_heuristic(self, env):
        return 0

    def points_heuristic(self, env):
        return env.player_points

    def a_star_search(self, env, heuristic):
        # a state = ( (levelstring, points, turn), [sequence] ) the level string can be used to create a new env and simulate
        open_list = util.PriorityQueue()
        open_list.push( ((env.level_string(), env.player_points, env.turn), []), heuristic(env) )
        closed_list = []
        current_state = ((env.level_string(), env.player_points, env.turn), [])
        num_endings = 0

        sim_env = ScavengerEnv(env.level_string(), False)
        while not open_list.isEmpty():
            current_state = open_list.pop()
            visited = False

            for i in closed_list:
                if i[0][0] == current_state[0][0] and i[0][1] == current_state[0][1]:
                #if i == current_state:
                    visited = True
                    break

            if not visited and current_state is not None:
                successors = env.get_successors()
                for s in successors:
                    # simulate next move in a new environment
                    sim_env.level = sim_env.generate_level(current_state[0][0])
                    sim_env.player_points = current_state[0][1]
                    sim_env.turn = current_state[0][2]
                    sim_env.move(s[1])

                    # at a certain point, the agent will ineviteably fail
                    # this point can be determined by the starve_distance
                    manhattan_distance = util.manhattanDistance(sim_env.player_position, sim_env.goal_position)
                    food_distances = []
                    for food in sim_env.food_positions:
                        food_distances.append(util.manhattanDistance(sim_env.player_position, food))
                    food_distances.append(manhattan_distance)

                    starve_distance = min(food_distances)
                    #print(f'starve dist = {starve_distance}')
                    if sim_env.done or sim_env.player_points <= starve_distance:
                        num_endings += 1
                        continue

                    # update the sequence of moves after this move
                    path = list()
                    for action in current_state[1]:
                        path.append(action)
                    path.append(s[1])

                    # update openlist with the new environment
                    new_state = ( (sim_env.level_string(), sim_env.player_points, sim_env.turn), path )
                    #print(f'In ({sim_env.player_position[1]}, {sim_env.player_position[0]}) move {s[1]} for potential score: {sim_env.player_points}')
                    open_list.push( new_state, heuristic(sim_env))
                # end for s in successors
            # end not visited...
            closed_list.append(current_state)
        #end while
        sequence = current_state[1]
        print(f'# calculated moves = {len(closed_list)} num leaves = {num_endings}')
        return sequence
