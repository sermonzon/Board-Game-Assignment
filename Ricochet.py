import pygame
from collections import deque
import random
import time

# Constants
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480
GRID_SIZE = 30
NUM_ROBOTS = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (59,131,189)
GREEN = (0,255,0)
YELLOW = (255,255,0)

players_colors = [RED, BLUE, YELLOW, GREEN]

class RicochetRobots:
    def __init__(self, size=16):
        self.size = size # size of the board (size x size)
        self.board = [[' ' for _ in range(size)] for _ in range(size)]  # the cells of the board are ' ' at first
        self.robots = {}  # dict to keep track of only the positions of the robots
        self.colored_robots = {}  # dict to keep track of the positions and colors of the robots
        self.target = None  # cell of the target
        self.walls = set()  # cells of the walls
        self.game_over = False   # True if the game is over
        self.target_color = None  # color of the target
        self.selected_robot = None  # when moving the robot by ourselves, this says which robot has been selected
        self.initial_positions = {}  # intial positions of the robots
        self.already_visited = [[]]  # dict with the positions already visited of the robots
        # Difference between self.robot, self.colored_robots, self.initial_robots and self.already_robot: 
        # self.robots: This attribute keeps track of the current positions of all robots at any given time during the game. It is updated whenever a robot moves.
        # self.colored_robots: Unlike self.robots, this attribute is mainly used for visualization purposes. It keeps track of the positions of robots only under specific conditions:
        #   1. When a path to the target has been found using BFS.
        #   2. When no path has been found using BFS, and the game randomly selects a robot to change its position to explore alternative paths.
        # self.initial_position: This attribute stores the initial positions of all robots at the start of the game. It is not updated during the game unless a random robot change occurs due to no path being found. 
        # self.already_visited: This attribute keeps track of all possible combinations of robot positions that have been explored during the search for a path using BFS. Each combination is recorded once it's explored to avoid revisiting the same position configurations. This helps prevent the algorithm from getting stuck in loops or redundant searches.

    # function to place walls randomly in the board (change number_of_walls to put more or less walls)
    def place_walls_random(self):
        number_of_walls = 50
        for _ in range(number_of_walls):
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            self.walls.add((x, y)) 

    def place_walls_1(self):
        # LEVEL 1
        mylist = [(0,9), (1,4), (1,7), (1,13), (1,15), (2,3), (2,5), (2,9), (2,10), (2,13), (3,1), (4,4), (5,4),
                        (5,6), (5,7), (5,13), (5,15), (6,13), (6,10), (0,7), (1,7), (6,7), (7,7), (10,7), (3,8), (11,8),
                        (8,9), (12,8), (13,8), (1,9), (12,9), (13,9), (3,10), (5,10), (10,10), (15,10), (0,10), (0,15),
                        (1,14), (0,13), (2,12), (2,13), (3,12), (6,15), (4,13), (6,6), (10,5), (9,12), (14,11), (13,15),(14,14)]
        for i in mylist:
            self.walls.add(i)

    def place_walls_2(self):  
        # LEVEL 2
        
        walls_list = [(4, 9), (3, 7), (14, 10), (5, 7), (0, 5), (9, 11), (11, 11), (13, 8),
                    (15, 11), (15, 8), (15, 14), (6, 11), (6, 5), (4, 2), (3, 0), (12, 9),
                    (14, 6), (3, 9), (5, 9), (8, 11), (9, 10), (9, 13), (0, 10), (10, 8), 
                    (13, 7), (1, 11), (0, 13), (7, 0), (1, 8), (15, 1), (13, 13), (7, 12), 
                    (3, 5), (5, 2), (9, 0), (10, 4), (9, 12), (11, 9), (10, 13), (7, 11), 
                    (1, 10), (13, 12), (6, 6), (7, 5), (15, 12)]
        for i in walls_list:
            self.walls.add(i)

    def place_walls_3(self):
        ### LEVEL 3 - Does not contain a valid solution
        walls_list = [(14, 4), (3, 4), (12, 10), (14, 1), (3, 10), (4, 15), (11, 2), (10, 0), 
            (2, 8), (2, 14), (6, 11), (7, 10), (3, 0), (12, 6), (4, 8), (4, 14), (3, 6), 
            (3, 15), (5, 12), (8, 8), (2, 4), (13, 4), (9, 13), (10, 8), (13, 1), (15, 4),
            (0, 13), (2, 10), (15, 7), (7, 6), (12, 11), (14, 5), (3, 11), (3, 14), (4, 13), 
            (1, 1), (9, 12), (13, 0), (9, 15), (8, 13), (2, 3), (15, 0), (15, 9), (6, 9)]
        for i in walls_list:
            self.walls.add(i)

    def place_walls_4(self):
            # LEVEL 4
            mylist = [(4,0), (0,3),(1,4), (3,7), (7,6), (6,9),(11,8),(10,10),(14,9),(13,15),(14,14),
                      (8,0),(12,0),(15,3),(15,6), (15,8),(14,0)]
            for i in mylist:
                self.walls.add(i)
        
    # function to place the target (this function first put a target in a random cell, and then it creates to walls next to it, so that
    # both walls form a corner and it is easier to find a solution )
    def place_target_random(self):
        x, y = random.randint(1, self.size - 2), random.randint(1, self.size - 2)
        # Randomly choose whether the first wall will be vertical or horizontal
        is_vertical = random.choice([True, False])
        if is_vertical:
            # If the first wall is vertical, place it to the left or right of the goal
            wall_x = x
            wall_y = random.choice([y - 1, y + 1])
        else:
            # If the first wall is horizontal, place it above or below the goal
            wall_x = random.choice([x - 1, x + 1])
            wall_y = y

        # Add the first wall
        self.walls.add((wall_x, wall_y))

        # Calculate the position of the second wall (forming a corner with the first wall)
        if is_vertical:
            # If the first wall is vertical, the second wall will be above or below the goal
            wall_x2 = random.choice([x - 1, x + 1])
            wall_y2 = y
        else:
            # If the first wall is horizontal, the second wall will be to the left or right of the goal
            wall_x2 = x
            wall_y2 = random.choice([y - 1, y + 1])

        # Add the second wall
        self.walls.add((wall_x2, wall_y2))
        self.target = (x, y)
        self.target_color = random.choice(players_colors)
    
    def place_target_1(self):
        ### LEVEL 1 ###
        self.target = (13,14)
        self.target_color = (255,0,0)

    def place_target_2(self):
        ### LEVEL 2 ###
        self.target = (4,1)
        self.target_color = (255,255,0) 

    def place_target_3(self):
        ### LEVEL 3 (non working) ###
        self.target = (10,3)
        self.target_color = (0,255,0)

    def place_target_4(self):
        ### LEVEL 4 ###
        self.target = (13,14)
        self.target_color = (255,0,0)


    # function to place robots randomly in the board
    def place_robots_random(self):
        for i in range(NUM_ROBOTS):
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            while (x, y) in self.robots.values() or (x, y) in self.walls or (x, y) == self.target:
                x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            self.robots[i] = (x, y)
            self.colored_robots[i] = (x, y, players_colors[i])
            self.initial_positions[i] = (x,y,players_colors[i])
            self.already_visited[0].append((x,y,players_colors[i]))

    def place_robots_1(self):
        ### LEVEL 1
        self.robots[0] = (6,3)
        self.robots[1] = (15,2)
        self.robots[2] = (9,2)
        self.robots[3] = (0,0)
        self.colored_robots[0] = (6,3,(255,0,0))
        self.colored_robots[1] = (15,2,(255,255,0))
        self.colored_robots[2] = (9,2,(0,255,0))
        self.colored_robots[3] = (0,0,(59,131,189))
        self.initial_positions[0] = (6,3,(255,0,0))
        self.initial_positions[1] = (15,2,(255,255,0))
        self.initial_positions[2] = (9,2,(0,255,0))
        self.initial_positions[3] = (0,0,(59,131,189))
        self.already_visited[0].append((6,3,(255,0,0)))
        
    def place_robots_2(self):
        ### LEVEL 2
        self.robots[0] = (15,0)
        self.robots[1] = (14,4)
        self.robots[2] = (1,1)
        self.robots[3] = (9,9)
        self.colored_robots[0] = (15,0,(255,255,0))
        self.colored_robots[1] = (14,4,(255,0,0))
        self.colored_robots[2] = (1,1,(0,255,0))
        self.colored_robots[3] = (9,9,(59,131,189))
        self.initial_positions[0] = (14,4,(255,0,0))
        self.initial_positions[1] = (15,0,(255,255,0))
        self.initial_positions[2] = (1,1,(0,255,0))
        self.initial_positions[3] = (9,9,(59,131,189))
        self.already_visited[0].append((15,0,(255,255,0)))
      
    def place_robots_3(self):
        ### LEVEL 3 - Does not contain a valid solution
        self.robots[0] = (8, 4)
        self.robots[1] = (3, 1)
        self.robots[2] = (11, 11)
        self.robots[3] = (7, 2)
        self.colored_robots[0] = (8, 4, (255, 0, 0))
        self.colored_robots[1] = (3, 1, (59, 131, 189))
        self.colored_robots[2] = (11, 11, (255, 255, 0))
        self.colored_robots[3] = (7, 2, (0, 255, 0))
        self.initial_positions[0] = (8, 4, (255, 0, 0))
        self.initial_positions[1] = (3, 1, (59, 131, 189))
        self.initial_positions[2] = (11, 11, (255, 255, 0))
        self.initial_positions[3] = (7, 2, (0, 255, 0))
        self.already_visited[0].append((8, 4, (255, 0, 0)))
  
    def place_robots_4(self):
            ### LEVEL 4
            self.robots[0] = (0,0)
            self.robots[1] = (15,2)
            self.robots[2] = (9,2)
            self.robots[3] = (6,4)
            self.colored_robots[0] = (0,0,(255,0,0))
            self.colored_robots[1] = (15,2,(255,255,0))
            self.colored_robots[2] = (9,2,(0,255,0))
            self.colored_robots[3] = (6,4,(59,131,189))
            self.initial_positions[0] = (0,0,(255,0,0))
            self.initial_positions[1] = (15,2,(255,255,0))
            self.initial_positions[2] = (9,2,(0,255,0))
            self.initial_positions[3] = (6,4,(59,131,189))
            self.already_visited[0].append((0,0,(255,0,0)))







    # draw the board - function used by AI and User
    def draw_board(self, screen):
        for i in range(self.size):
            for j in range(self.size):
                pygame.draw.rect(screen, WHITE, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                for _, (robot_x, robot_y, color) in self.colored_robots.items():
                    if (i, j) == (robot_x, robot_y):
                        pygame.draw.circle(screen, color, (j * GRID_SIZE + GRID_SIZE // 2, i * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 3)
                if (i, j) == self.target:
                    pygame.draw.rect(screen, self.target_color, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                elif (i, j) in self.walls:
                    pygame.draw.rect(screen, GRAY, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # check if there is a colision with 2 different robots - function used by AI and User
    def check_collision(self, position, robot):
        for robot_id, pos in self.robots.items():
            if pos == position and robot_id != robot:
                return True
        return False
    
    # function to move robots when the User is playing the game
    def move_robot(self, direction):
        if not self.game_over and self.selected_robot is not None:
            x, y = self.robots[self.selected_robot]
            if direction == 'up':
                while x > 0 and (x-1, y) not in self.walls and not self.check_collision(self.selected_robot, (x - 1, y)):
                    x -= 1
            elif direction == 'down':
                while x < self.size -1 and (x + 1, y) not in self.walls and not self.check_collision(self.selected_robot, (x + 1, y)):
                    x += 1
            elif direction == 'left':
                while y > 0 and (x, y - 1) not in self.walls and not self.check_collision(self.selected_robot, (x, y - 1)):
                    y -= 1
            elif direction == 'right':
                while y < self.size - 1 and (x, y + 1) not in self.walls and not self.check_collision(self.selected_robot, (x, y + 1)):
                    y += 1
            self.robots[self.selected_robot] = (x, y)
            color = self.colored_robots[self.selected_robot][2]
            self.colored_robots[self.selected_robot] = (x, y, color)

            if (x, y) == self.target and color == self.target_color:
                self.game_over = True
    
    # function used by our AI to move the robot
    def move_in_direction(self, start_pos, direction, current_robot):
        # Move from start_pos in the specified direction until an obstacle is hit
        x, y = start_pos
        if direction == 'up':
            while x > 0 and (x-1, y) not in self.walls and (x-1, y) not in self.robots.values():
                x -= 1
        elif direction == 'down':
            while x < self.size-1 and (x+1, y) not in self.walls and (x+1, y) not in self.robots.values():
                x += 1
        elif direction == 'left':
            while y > 0 and (x, y-1) not in self.walls and (x, y-1) not in self.robots.values():
                y -= 1
        elif direction == 'right':
            while y < self.size-1 and (x, y+1) not in self.walls and (x, y+1) not in self.robots.values():
                y += 1
        self.robots[current_robot] = (x,y)
        return (x, y)

    # apply BFS for our AI
    def bfs(self):
        target_robot_ids = [robot_id for robot_id, (_, _, color) in self.initial_positions.items() if color == self.target_color]

        if not target_robot_ids:
            return None  # No robot with the target color

        initial_positions = {robot_id: self.initial_positions[robot_id][:2] for robot_id in target_robot_ids}
        queue = deque([(initial_positions, 0, [])])
        visited = set([tuple(initial_positions.values())])
        i = 0

        while queue:
            current_positions, steps, path = queue.popleft()
            if any(pos == self.target for pos in current_positions.values()):
                self.colored_robots = self.robots
                print("State generated: ",i)
                return path

            for robot_id, current_pos in current_positions.items():
                for direction in ['up', 'down', 'left', 'right']:
                    new_pos = self.move_in_direction(current_pos, direction, robot_id)
                    new_positions = {k: v for k, v in current_positions.items()}
                    new_positions[robot_id] = new_pos
                    i+=1
                    if tuple(new_positions.values()) not in visited:
                        visited.add(tuple(new_positions.values()))
                        queue.append((new_positions, steps + 1, path + [(direction, new_pos)]))

        return None  # No path found

    # apply DFS for our AI
    def dfs(self):
        target_robot_id = None
        for robot_id, (_, _, color) in self.initial_positions.items():
            if color == self.target_color:
                target_robot_id = robot_id
                break

        if target_robot_id is None:
            return None  # No robot with the target color

        queue = deque([((target_robot_id, self.initial_positions[target_robot_id][:2]), 0, [])])
        visited = set([self.initial_positions[target_robot_id]])
        i = 0

        while queue:
            (current_robot_id, current_pos), steps, path = queue.popleft()
            if current_pos == self.target:
                print("States generated: ",i)
                return path

            for direction in ['up', 'down', 'left', 'right']:
                i+=1
                new_pos = self.move_in_direction(current_pos, direction, target_robot_id)
                if new_pos not in visited:
                    visited.add(new_pos)
                    queue.appendleft(((current_robot_id, new_pos), steps + 1, path + [(direction, new_pos)]))

        return None  # No path found
    
    # apply Greedy Best-First Search algorithm with Manhattan distance heuristic for our AI
    def greedy_best_first_search(self):
        target_robot_id = None
        for robot_id, (_, _, color) in self.initial_positions.items():
            if color == self.target_color:
                target_robot_id = robot_id
                break

        if target_robot_id is None:
            return None  # No robot with the target color

        start_node = (target_robot_id, self.initial_positions[target_robot_id][:2])
        goal_node = self.target

        # Initialize open and closed lists
        open_list = deque([start_node])
        closed_list = set()

        # Dictionary to store the parent node for each visited node
        parents = {}
        node_number = 0

        while open_list:
            # Get the node with the lowest heuristic estimate
            current_node = min(open_list, key=lambda x: self.calculate_heuristic(x[1], goal_node))

            open_list.remove(current_node)

            # Check if the current node is the goal node
            if current_node[1] == goal_node:
                return self.reconstruct_path(parents, direction, current_node[1])

            # Expand the current node
            for direction in ['up', 'down', 'left', 'right']:
                new_pos = self.move_in_direction(current_node[1], direction, current_node[0])
                new_node = (current_node[0], new_pos)

                if new_pos is None:
                    continue

                # Check if the new node is already in the closed list
                if new_node in closed_list:
                    continue

                # Add the new node to the open list with the heuristic estimate
                open_list.append(new_node)

                # Set the parent node for the new node
                parents[node_number] = (direction, current_node[1])
                node_number += 1

            # Add the current node to the closed list
            closed_list.add(current_node)

        return None  # No path found


    # apply A* algorithm with Manhattan distance heuristic for our AI
    def A_star(self):
        target_robot_id = None
        for robot_id, (_, _, color) in self.initial_positions.items():
            if color == self.target_color:
                target_robot_id = robot_id
                break

        if target_robot_id is None:
            return None  # No robot with the target color
        start_node = (target_robot_id, self.initial_positions[target_robot_id][:2])
        #print("This is start node: ",start_node)
        goal_node = self.target
        # Initialize open and closed lists
        open_list = deque([start_node])
        closed_list = set()

        # Dictionary to store the parent node for each visited node
        parents = {}
        node_number = 0

        while open_list:
            # Get the node with the lowest combined cost (actual cost + heuristic estimate)
            current_node = min(open_list, key=lambda x: self.calculate_combined_cost(x, goal_node))
            open_list.remove(current_node)

             # Check if the current node is the goal node
            if current_node[1] == goal_node:
                return self.reconstruct_path(parents, direction, current_node[1])
            
            # Expand the current node
            for direction in ['up', 'down', 'left', 'right']:
                new_pos = self.move_in_direction(current_node[1], direction, current_node[0])
                new_node = (current_node[0], new_pos)

                if new_pos is None:
                    continue

                # Check if the new node is already in the closed list
                if new_node in closed_list:
                    continue

                # Add the new node to the open list with the combined cost
                open_list.append(new_node)

                # Set the parent node for the new node
                parents[node_number] = (direction, current_node[1])
                node_number += 1
                
            # Add the current node to the closed list
            closed_list.add(current_node)

        return None  # No path found
    
    # function to reconstruct the path when it finds a solution for our AI
    def reconstruct_path(self,parents, direction, current_node):
        sorted_dict = dict(sorted(parents.items()))
        previous_value = None
        previous_value2 = None
        path = []
        for value in sorted_dict.values():
            if value[0] != previous_value and value[1] != previous_value2:
                path.append(value)
            previous_value = value[0]
            previous_value2 = value[1]
        path.append((direction, current_node))  # add goal node to the path
        print("States generated: ",len(path))
        return path                 
    
    def calculate_combined_cost(self, node, goal_node):
        actual_cost = self.calculate_actual_cost(node[1], goal_node)
        heuristic = self.calculate_heuristic(node[1], goal_node)
        return actual_cost + heuristic

    def calculate_actual_cost(self, current_pos, new_pos):
        # Calculate the actual cost from the current position to the new position
        actual_cost = abs(current_pos[0] - new_pos[0]) + abs(current_pos[1] - new_pos[1])
        return actual_cost

    def calculate_heuristic(self, node, goal_node):
        # Calculate the heuristic estimate (Manhattan distance) of the cost from the node to the goal node
        heuristic = abs(node[0] - goal_node[0]) + abs(node[1] - goal_node[1])
        return heuristic

    # function to move other robots (non-main one) and then saved it in the intial positions (as well as the colored_robots) for our AI
    def move_robot2(self, robot, direction):
        if not self.game_over:
            x, y = self.initial_positions[robot][:2]
            if direction == 'up':
                while x > 0 and (x-1, y) not in self.walls and not self.check_collision(robot, (x - 1, y)):
                    x -= 1
            elif direction == 'down':
                while x < self.size -1 and (x + 1, y) not in self.walls and not self.check_collision(robot, (x + 1, y)):
                    x += 1
            elif direction == 'left':
                while y > 0 and (x, y - 1) not in self.walls and not self.check_collision(robot, (x, y - 1)):
                    y -= 1
            elif direction == 'right':
                while y < self.size - 1 and (x, y + 1) not in self.walls and not self.check_collision(robot, (x, y + 1)):
                    y += 1
            
            color = self.colored_robots[robot][2]  # take the color of the robot
            self.initial_positions[robot] = (x, y, color)
            self.colored_robots[robot] = (x, y, color)

            if (x, y) == self.target and color == self.target_color:
                self.game_over = True

    # function that change the selected robot (non-main one) for our AI
    def change_robot(self):
        target_robot_id = None
        for robot_id, (_, _, color) in self.initial_positions.items():
            if color == self.target_color:
                target_robot_id = robot_id
        new_choices = [x for x in [0,1,2,3] if x != target_robot_id]
        robot = random.choice(new_choices)
        direction = random.choice(['up','down','right','left'])
        self.move_robot2(robot, direction)
    
        # see if that configuration of initial positions have been sees before. For that, all the initial positions will be save in self.already_visited
        positions = []
        for _ , (x,y,color) in self.initial_positions.items():
            positions.append((x,y,color))
        if positions in self.already_visited:
            self.change_robot()
        
    
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ricochet Robots")
    game = RicochetRobots()

    # Change the next 3 lines to select different levels (existing levels: random, 1, 2, 3, 4)
    game.place_walls_4()
    game.place_robots_4()
    game.place_target_4()

    clock = pygame.time.Clock()
    screen.fill(WHITE)
    game.draw_board(screen)
    pygame.display.flip()
    clock.tick(60)
    font = pygame.font.Font(None, 36)
    User_play = False # Change to True if you want the User to play
    AI_play = True # Change to True if you want the AI to play
    start_time = time.time_ns()

    # AI is playing
    while AI_play:
        path = game.dfs() # DFS algorithm
        #path = game.bfs() # BFS algorithm
        #path = game.A_star() # A* algorithm
        #path = game.greedy_best_first_search() # GBFS algorithm
        if path is not None:
            end_time = time.time_ns()
            elapsed_time = end_time - start_time
            print("Time taken to find a solution:", elapsed_time, "nanoseconds")
            AI_play = False
            i = 0
            # Draw the path on the screen
            for direction, pos in path:
                pygame.draw.circle(screen, BLACK, (pos[1] * GRID_SIZE + GRID_SIZE // 2, pos[0] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2)
                i += 1
                text_surface = font.render(str(i), True, RED)
                text_rect = text_surface.get_rect(center=(pos[1] * GRID_SIZE + GRID_SIZE // 2, pos[0] * GRID_SIZE + GRID_SIZE // 2))
                screen.blit(text_surface, text_rect)
                pygame.display.flip()
                pygame.time.delay(1000)
            
        else:
            # if a path has not been found, it calls game.change_robot() that will moves other robots (non-main one) and start looking for a solution again
            print("Solution not found, I will try to move other robots")
            game.change_robot()   
            clock = pygame.time.Clock()
            screen.fill(WHITE)
            game.draw_board(screen)
            pygame.display.flip()
            passed_time = time.time_ns()-start_time
            if passed_time>300000000000:
                print("I did not find any solution in the past 5 minutes")
                AI_play = False

    moves = 0
    # User is playing
    while User_play:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                User_play = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.move_robot('up')
                    moves += 1
                elif event.key == pygame.K_DOWN:
                    game.move_robot('down')
                    moves += 1
                elif event.key == pygame.K_LEFT:
                    game.move_robot('left')
                    moves += 1
                elif event.key == pygame.K_RIGHT:
                    game.move_robot('right')
                    moves += 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                grid_pos = (mouse_pos[1] // GRID_SIZE, mouse_pos[0] // GRID_SIZE)
                for robot_id, robot_pos in game.robots.items():
                    if robot_pos == grid_pos:
                        game.selected_robot = robot_id
        screen.fill(WHITE)
        game.draw_board(screen)
        pygame.display.flip()
        clock.tick(60)

        if game.game_over: 
            elapsed_time = time.time_ns() - start_time
            print("Time taken to find a solution:", elapsed_time, "nanoseconds")
            font = pygame.font.Font(None, 36)
            text = font.render("You Win!", True, BLACK)
            print("User takes ",moves, "moves to find a solution")
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(5000)
            break

    pygame.time.wait(5000) # visualization time before closing the game
    pygame.quit()

if __name__ == "__main__":
    main()

