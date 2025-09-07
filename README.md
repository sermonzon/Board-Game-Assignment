####### RICOCHET ROBOTS GAME #######
Ricochet Robots is a challenging puzzle game where the goal is to navigate robots through a maze to a target location. This Python version uses the Pygame library for its graphical interface and offers various algorithms for robot navigation.

####### Prerequisites #######
Before you start, ensure you have the following installed:

- Python 3.6 or newer
- pip (Python package installer)
- pygame library (it can be installed using pip)

###### Selecting Levels ######
The game includes several levels, as well as a feature for random level generation. To select a level, modify the following lines in the main() function:

game.place_walls_4()  # For wall placement
game.place_robots_4()  # For robot placement
game.place_target_4()  # For target placement

Available methods for each category are:

- Walls: place_walls_random(), place_walls_1(), place_walls_2(), place_walls_3(), place_walls_4()
- Robots: place_robots_random(), place_robots_1(), place_robots_2(), place_robots_3(), place_robots_4()
- Target: place_target_random(), place_target_1(), place_target_2(), place_target_3(), place_target_4()

Replace the method number with the desired level number or use the random methods for a randomly generated setup.

###### Selecting the Pathfinding Algorithm ######
This game supports multiple pathfinding algorithms. To select an algorithm, uncomment the corresponding line in the "while AI_play:" loop:

path = game.dfs()  # Depth-First Search
# path = game.bfs()  # Breadth-First Search
# path = game.A_star()  # A* Search
# path = game.greedy_best_first_search()  # Greedy Best-First Search

By default, the Depth-First Search (DFS) algorithm is used.

###### Playing the Game ######
The game can be played in two modes: AI or user.

AI Play: To let the AI solve the puzzle, ensure AI_play is set to "True" and User_play is set to "False".
User Play: To play the game yourself, set User_play to "True" and AI_play to "False". Select the robot by clicking on it and use the arrow keys to move it.

###### Game Over ######
The game concludes when the target is reached with the correct robot. For AI mode, the path taken will be displayed on the screen. For user mode, the game will display a "You Win!" message.
