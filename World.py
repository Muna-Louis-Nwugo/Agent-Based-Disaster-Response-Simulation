import Agents
import numpy as np
import random

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
        self.occupant = None #Agent

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

        #Note: the grid map is to be made up of a 2d numpy array of Cell objects, to help each cell store data more effectively
    """

    def __init__(self, num_civilians: int, num_paramedics: int, num_firefighters: int, map: np.ndarray[Cell]): # type: ignore
        self.num_civilians: int = num_civilians
        self.num_paramedics: int = num_paramedics
        self.num_firefighters: int = num_firefighters
        """
        #TODO: Write initialization method for and self.road_graph
        """
        self.map: np.ndarray[Cell] = map # type: ignore
        self.road_graph: dict = self.init_road_graph()

        self.agent_spawn(self.num_civilians, Agents.Civilian)
        """ self.agent_spawn(self.num_paramedics, Agents.Paramedic)
        self.agent_spawn(self.num_firefighters, Agents.Firefighter) """

    
    
    # Return a hashmap of this world's traversible cells
    def init_road_graph(self) -> dict:
        """
        This function produces the list of the traversible cells (roads) in this world. It does so by visiting each cell in this world, and then iterating through a list of possible neighbours,
        adding all valid neighbours to a list. This list is then assigned to the original cell's key.
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
        This function spawns random agents onto the grid by generating random indeces and placing agents in them until the desired number of agents have been placed
        """

        road_list: list[tuple] = list(self.road_graph.keys())

        while num_agents > 0:
            rand_num = random.randrange(0, len(road_list))
            desired_cell = road_list[rand_num]

            if self.map[desired_cell[0], desired_cell[1]].occupant is not None: # type: ignore #checks if a cell is already occupied
                continue
            else:
                self.map[desired_cell[0], desired_cell[1]].occupant = agent_type(desired_cell, None) # type: ignore #TODO: build method to pass through agent perception
                num_agents -= 1
