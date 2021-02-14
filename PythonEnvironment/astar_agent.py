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
        self.sequence = self.a_star_search(env)
        self.move_count = 0

    def suggest_move(self, env):
        #seq = self.a_star_search(env)
        move = self.sequence[self.move_count]
        self.move_count += 1
        return move

    def a_star_search(self, env):
        # a state = ( ScavengerEnv, [sequence] ) the level string can be used to create a new env and simulate
        # IDEA: create a game state that is used to modify the existing environment
        # new state = ( ((x,y), points, [enemy_positions], [food_positions], turn), [sequence] )
        open_list = util.PriorityQueue()
        open_list.push( (env, []), env.player_points )
        closed_list = []
        current_state = (env, [])
        num_endings = 0

        while not open_list.isEmpty():
            current_state = open_list.pop()
            visited = False

            for i in closed_list:
                if i[0].level_string() == current_state[0].level_string() and i[0].player_points == current_state[0].player_points:
                    visited = True
                    break

            if not visited and current_state is not None:
                successors = env.get_successors()
                for s in successors:
                    # simulate next move in a new environment
                    sim_env = current_state[0].clone()
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
                        #print(f'terminal state with points {sim_env.player_points}')
                        if sim_env.done:
                            print(f'win path found with points = {sim_env.player_points}')
                        num_endings += 1
                        continue

                    # update the sequence of moves after this move
                    path = list()
                    for action in current_state[1]:
                        path.append(action)
                    path.append(s[1])

                    # update openlist with the new environment
                    new_state = ( (sim_env), path )
                    #print(f'In ({sim_env.player_position[1]}, {sim_env.player_position[0]}) move {s[1]} for potential score: {sim_env.player_points}')
                    open_list.push( (sim_env, path), sim_env.player_points)
                # end for s in successors
            # end not visited...
            closed_list.append(current_state)
        #end while
        sequence = current_state[1]
        print(f'# calculated moves = {len(closed_list)} num leaves = {num_endings}')
        return sequence
