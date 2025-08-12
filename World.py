import Agents
import numpy as np
import random
import time

"""
World Module - Main simulation engine for the Urban Catastrophe Simulation.

This module contains the World class which manages the spatial environment, agent population, 
and simulation state. It handles:
- Grid-based city representation with roads, buildings, and intersections
- Agent spawning, movement, and collision detection
- Simulation tick updates and event dispatching
- Spatial queries for pathfinding and agent perception
- Communication between agents and environment

The World class serves as the central coordinator, maintaining the 100x100 cell grid
and orchestrating all agent behaviors during catastrophic events.
"""

class Cell():
    """
    The Cell class represents each cell in the 100x100 grid. It stores information about what type of cell it is
    (road or building) and whhich agent is currently occupying the cell.
    """
    def __init__(self, is_road: bool):
        self.is_road: bool = is_road
        self.occupant: Agents.Agent = None  # type: ignore

class World():
    """
    The World class acts as the main simulation engine. It harbors the map agents traverse, the agents themselves,
    And the information that every agent needs to function properly.

    Properties: 
        num_civilians -> Number of civilians on the map
        num_paramedics -> Number of paramedics on the map
        num_firefighters -> Number of firefighters on the map
        cell_occupants -> Which cell is occupied and by which agent
        map -> the grid map that the agents traverse along
        road_graph -> a graphical representation of the grid map, except only including roads. Enables pathfinding around buildings
        agents -> list of all agents

        #Note: the grid map is to be made up of a 2d numpy array of Cell objects, to help each cell store data more effectively
    """

    def __init__(self, num_civilians: int, num_paramedics: int, num_firefighters: int, map: np.ndarray[Cell]): # type: ignore
        self.num_civilians: int = num_civilians
        self.num_paramedics: int = num_paramedics
        self.num_firefighters: int = num_firefighters
        self.map: np.ndarray[Cell] = map # type: ignore
        self.road_graph: dict = self.init_road_graph()
        self.agents: list[Agents.Agent] = []

        self.agent_spawn(self.num_civilians, Agents.Civilian)
        """ self.agent_spawn(self.num_paramedics, Agents.Paramedic)
        self.agent_spawn(self.num_firefighters, Agents.Firefighter) """

    
    
    # Return a hashmap of this world's traversible cells
    def init_road_graph(self) -> dict:
        """
        Constructs an adjacency graph of all traversable road cells for pathfinding.
        
        Examines each cell in the grid and, for road cells, identifies all valid 
        neighboring road cells within a 1-cell radius (8-directional movement). 
        The resulting graph maps each road cell's coordinates to a list of 
        accessible neighbor coordinates.
        
        Returns:
            dict: Adjacency graph where keys are road cell coordinates (y, x) and 
                values are lists of neighboring road cell coordinates that can 
                be reached in one move.
                
        Example:
            {(0, 1): [(0, 2), (1, 1), (1, 2)],
            (0, 2): [(0, 1), (0, 3), (1, 2)], ...}

        FIXME: Remove graph connections for roads that require an intersection in between
        """
        # container for our graph, to be filled in
        graph: dict = {}
        
        #total possible neighbours around a cell
        possible_neighbours: list[tuple[int, int]] = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, 1), (1, -1), (0, -1)]

        #looping through cells, populating graph
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x].is_road:
                    #All valid
                    valid_neighbours = []

                    for dy, dx in possible_neighbours:
                        ny, nx = dy + y, dx + x

                        if ny < self.map.shape[0] and nx < self.map.shape[1] and ny >= 0 and nx >= 0:
                            if self.map[ny][nx].is_road:
                                valid_neighbours.append((ny, nx))
                    

                    graph[(y, x)] = valid_neighbours
        
        return graph

    
    # EFFECT: Spawns agents in the grid
    def agent_spawn(self, num_agents: int, agent_type: type) -> None:
        """
        Spawns the specified number of agents randomly on available road cells.
        
        Iterates through random road positions until all agents are placed. Ensures
        no two agents occupy the same cell during initialization. Each agent receives
        its initial perception and movement options based on spawn location.
        
        Args:
            num_agents: Number of agents to spawn
            agent_type: Class type of agent to spawn (e.g., Agents.Civilian)
        
        Side Effects:
            - Adds agents to self.agents list
            - Updates cell occupancy in self.map
            - Sets initial perception for each spawned agent
        """

        road_list: list[tuple] = list(self.road_graph.keys())

        while num_agents > 0:
            rand_num = random.randrange(0, len(road_list))
            desired_cell = road_list[rand_num]

            if self.map[desired_cell[0], desired_cell[1]].occupant is not None: # type: ignore #checks if a cell is already occupied
                continue
            else:
                new_agent = agent_type(desired_cell, self.road_graph)
                self.set_perception(new_agent)
                self.map[desired_cell[0], desired_cell[1]].occupant = new_agent # type: ignore
                self.agents.append(new_agent)
                num_agents -= 1
    
    
    # EFFECT: initializes agent perception
    def set_perception(self, agent: Agents.Agent) -> None:
        """
        Updates an agent's perception array with their surrounding environment.
        
        Extracts a 7x7 grid centered on the agent's current position, giving them
        visibility 3 cells in each direction. Handles edge cases where agents are
        near map boundaries by numpy's automatic bounds clipping.
        
        Args:
            agent: The agent whose perception needs updating
        
        Side Effects:
            - Updates agent.perception with current surrounding grid
        """
        y, x = agent.location

        perception: np.ndarray = self.map[y-3:y+4, x-3:x+4]

        agent.perception = perception
    
    #EFFECT: updates every agent on the grid
    def update(self):
        """
        Executes one simulation tick, updating all agent positions and states.
        
        For each agent: captures current position, calls agent's update method
        (which may change position), updates grid occupancy, refreshes perception
        based on new position, and updates available movement options. Does not
        handle collision detection in current implementation.
        
        Side Effects:
            - Updates all agent positions
            - Updates cell occupancy in self.map
            - Refreshes agent perceptions
        
        TODO: Manage collision detection
        (Actually, it might be better to manage Collision Detection within the agent itself)
        """

        for agent in self.agents:
            old_loc = agent.location
            agent.update()
            new_loc = agent.location

            self.map[old_loc[0], old_loc[1]].occupant = None # type: ignore
            self.map[new_loc[0], new_loc[1]].occupant = agent # type: ignore

            self.set_perception(agent)


    # Draws map
    def draw(self) -> None:
        """
        Renders the current simulation state to console using ASCII characters.
        
        Displays a grid representation where:
        - '█' represents buildings (non-traversable)
        - '·' represents empty roads
        - 'C' represents civilians
        - 'P' represents paramedics (when implemented)
        - 'F' represents firefighters (when implemented)
        
        Useful for debugging agent movement and initial testing before 
        implementing full graphical visualization.
        
        Output:
            Prints grid to console with coordinate labels
        """
        print("\n  ", end="")
        # Print column numbers
        for x in range(len(self.map[0])):
            print(f"{x} ", end="")
        print()
        
        # Print each row
        for y in range(len(self.map)):
            print(f"{y} ", end="")
            for x in range(len(self.map[y])):
                cell = self.map[y][x]
                if not cell.is_road:
                    print("█ ", end="")
                elif cell.occupant is None:
                    print("· ", end="")
                elif isinstance(cell.occupant, Agents.Civilian):
                    print("C ", end="")
                # Add more agent types as needed
                else:
                    print("? ", end="")
            print()

if __name__ == "__main__": 
    # True = road, False = building
    test_grid = [
        [False, True,  True,  False, False, False, True,  True,  True,  False],
        [False, True,  True,  False, False, False, True,  False, True,  False],
        [False, True,  True,  True,  True,  True,  True,  False, True,  False],
        [False, False, False, False, False, False, False, False, True,  False],
        [True,  True,  True,  True,  True,  True,  True,  True,  True,  False],
        [True,  False, False, False, False, False, False, False, True,  False],
        [True,  True,  True,  True,  False, False, True,  True,  True,  False],
        [False, False, False, True,  False, False, True,  False, False, False],
        [True,  True,  True,  True,  False, False, True,  True,  True,  True],
        [False, False, False, False, False, False, False, False, False, False]
    ]

    # Convert to numpy array of Cell objects
    map_array = np.empty((10, 10), dtype=object)
    for y in range(10):
        for x in range(10):
            map_array[y, x] = Cell(test_grid[y][x])

    # Create world
    world = World(num_civilians=5, num_paramedics=0, num_firefighters=0, map=map_array) #type: ignore

    for i in range(10):
        world.update()
        world.draw()
        time.sleep(1) 