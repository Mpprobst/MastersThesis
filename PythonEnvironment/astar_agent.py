"""
astar_agent.py
Purpose: implements an agent that moves optimally in the level
Author: Michael Probst
"""
import random
import util
from scavenger_env import ScavengerEnv
import timeit
MOVES = ['U', 'D', 'L', 'R']

class AstarAgent():
    def __init__(self, start_score, env):
        self.reward = start_score
        #self.sequence = self.a_star_search(env, self.null_heuristic)
        self.move_count = 0

    def suggest_move(self, env):
        seq = self.a_star_search(env, self.optimal_heuristic)
        move = 'U'
        if len(seq) > 0:
            move = seq[0]
        #move = self.sequence[self.move_count]
        self.move_count += 1
        return move

    def null_heuristic(self, env, offset=0):
        return 0

    # the heuristic needs to return a small value if it is optimal.
    # because large score is optimal, the inverse will look better.
    # if the score is negative, the agent has lost, but we don't the lowest
    # value to be considered optimal, so we set lose states to a value of 100
    def points_heuristic(self, env, offset=0):
        points = env.player_points
        if points > 0:
            points = 0.01
        return float(1/points)

    # optimal gameplay gets as much food as possible in the fewest moves possible
    # while avoiding enemies
    def optimal_heuristic(self, env, offset=0):
        # maximize distance from enemies.
        max_dist = util.manhattanDistance( (env.level_height-1, 0), env.goal_position )
        total_dist = 0
        for enemy in env.enemy_positions:
            total_dist += max_dist - (util.manhattanDistance(env.player_position, enemy))
        return offset #+ total_dist

    def a_star_search(self, env, heuristic):
        # a state = ( (levelstring, points, turn), [sequence] ) the level string can be used to create a new env and simulate
        open_list = util.PriorityQueue()
        open_list.push( ((env.level_string(), env.player_points, env.turn), [], heuristic(env)), heuristic(env) )
        closed_list = []
        current_state = ((env.level_string(), env.player_points, env.turn), [], heuristic(env))
        num_endings = 0
        times = []
        start_time = timeit.default_timer()
        sim_env = ScavengerEnv(env.level_string(), False)
        while not open_list.isEmpty():
            current_state = open_list.pop()
            sim_env.player_points = current_state[0][1]
            sim_env.turn = current_state[0][2]
            sim_env.update_level(current_state[0][0])

            visited = False
            if sim_env.done or timeit.default_timer() - start_time > 30:
                break

            for i in closed_list:
                if i[0][0] == current_state[0][0] and i[0][1] == current_state[0][1]:
                    visited = True
                    break

            if not visited and not sim_env.done and current_state is not None:
                successors = env.get_successors(sim_env.player_position)
                for s in successors:
                    # simulate next move in a new environment
                    starttime = timeit.default_timer()
                    sim_env.player_points = current_state[0][1]
                    sim_env.turn = current_state[0][2]
                    sim_env.update_level(current_state[0][0])
                    #sim_env.level = sim_env.generate_level(current_state[0][0])
                    #print(f'level update time: {timeit.default_timer() - starttime}')
                    times.append(timeit.default_timer() - starttime)

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
                    if sim_env.player_points < starve_distance:
                        num_endings += 1
                        continue

                    # update the sequence of moves after this move
                    path = list()
                    for action in current_state[1]:
                        path.append(action)
                    path.append(s[1])
                    if len(path) >= 18:
                        continue
                    # update openlist with the new environment
                    priority = current_state[2] + heuristic(sim_env, s[2])
                    new_state = ( (sim_env.level_string(), sim_env.player_points, sim_env.turn), path,  priority)
                    #print(f'pushing to open list: {new_state[1]}, {new_state[2]}')
                    #print(f'In ({sim_env.player_position[1]}, {sim_env.player_position[0]}) move {s[1]} for potential score: {sim_env.player_points}, heuristic: ')
                    open_list.push(new_state, priority)
                # end for s in successors
            # end not visited...
            closed_list.append(current_state)
        #end while
        sequence = current_state[1]
        sequence_string = ""
        for s in sequence:
            sequence_string += s
        #print(f'sequence: {sequence_string} has heuristic value of: {current_state[2]}')
        #print(f'# calculated moves = {len(closed_list)} num leaves = {num_endings} avg computation time: {sum(times) / len(times)}')
        return sequence
