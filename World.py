from Agents import Civilian
import numpy as np

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
        cell_occupants -> Which cell is occupied and by which agent
        map -> the grid map that the agents traverse along
        map_graph -> a graphical representation of the grid map, except only including roads. Enables pathfinding around buildings

        #Note: the grid map is to be made up of a 2d numpy array of Cell objects, to help each cell store data more effectively
    """

    def __init__(self, num_civilians: int, map: np.ndarray[Cell]):
        self.num_civilians: int = num_civilians
        """
        #TODO: Write initialization method for and self.map_graph
        """
        self.map: np.ndarray[Cell] = map
        self.map_graph: dict = self.init_map_graph()

    # Return a hashmap of traversible cells
    def init_map_graph(self) -> dict:
        # container for our graph, to be filled in
        graph: dict = {}
        
        #total possible neighbours around a cell
        possible_neighbours: tuple[int] = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, 1), (1, -1), (0, -1)]

        #looping through cells, populating graph
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x].is_road:
                    real_neighbours = []

                    for dy, dx in possible_neighbours:
                        ny, nx = dy + y, dx + x

                        if ny < self.map.shape[0] and nx < self.map.shape[1] and ny >= 0 and nx >= 0:
                            if self.map[ny][nx].is_road:
                                real_neighbours.append((ny, nx))
                    
                    real_neighbours = np.array(real_neighbours) #updates variable to numpy array

                graph[(y, x)] = real_neighbours
                            

                    

