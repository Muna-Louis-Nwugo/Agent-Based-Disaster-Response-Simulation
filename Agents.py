import numpy as np
from enum import Enum
from abc import ABC, abstractmethod
import math
import heapq


"""
Agents Module - Autonomous entities for the Urban Catastrophe Simulation.

This module contains agent classes that populate and navigate the urban environment.
It handles:
- Agent state management (health, patterns, goals)
- Movement and pathfinding execution
- Perception and decision-making logic
- State transitions during catastrophic events
- Inter-agent awareness and collision avoidance

Agent types include Civilians, Paramedics, and Firefighters, each with distinct
behaviors and priorities during emergency scenarios.
"""

class Agent(ABC):
    def __init__(self, location: tuple, road_graph: dict, target: tuple):
        self.location: tuple = location
        self.perception: np.ndarray = None # type: ignore
        self.road_graph: dict = road_graph
        self.target = target
        self.path = self.find_path(self.target)

    @abstractmethod
    def update(self):
        pass

    # calculates this agent's path to a target
    def find_path(self, target: tuple) -> list[tuple]:

        """
        Calculates the optimal path from the agent's current location to a target using A* algorithm.
        
        Uses Chebyshev distance heuristic for 8-directional grid movement where all moves 
        (including diagonal) have equal cost. Explores nodes based on f-score (g + h) where
        g is distance from start and h is heuristic estimate to target.
        
        Args:
            target: Tuple (y, x) representing the destination coordinates on the grid
        
        Returns:
            list: Ordered list of tuples [(y1, x1), (y2, x2), ...] representing the path
                from current location to target. Returns empty list if no path exists.
                
        Implementation:
            - Maintains g_score dict tracking best known distance from start to each node
            - Uses min-heap priority queue for efficient node exploration
            - came_from dict enables path reconstruction after target is found
        """
        
        #HAD TO LEARN GSCORE TRACKING PATTERN, MY ORIGINAL SOLUTION WAS SO SCUFFED

        # Initialize g_score (keeps track of distance to nodes)
        g_score = {}
        g_score[self.location] = 0
        
        # Priority queue
        to_be_visited = []
        heapq.heappush(to_be_visited, (0, self.location))
        
        # Track path
        came_from = {}
        
        # A* algorithm
        while to_be_visited:
            current_f, current = heapq.heappop(to_be_visited)  # current_f not needed after pop
            
            if current == target:
                return self.finish_path([], target, came_from)
            
            for neighbor in self.road_graph[current]:
                heuristic = max(abs(neighbor[0] - target[0]), abs(neighbor[1] - target[1]))
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic
                    heapq.heappush(to_be_visited, (f, neighbor))
                    came_from[neighbor] = current

    
    #Find path helper
    def finish_path(self, completed_path: list, val: tuple, came_from: dict) -> list[tuple]:
        """
        Recursively reconstructs the path from target to starting location using the came_from mapping.
        
        Traces backwards through the came_from dictionary, building the path in reverse order,
        then flips it to create start->target ordering.
        
        Args:
            completed_path: List to accumulate path nodes during recursion (typically starts empty)
            val: Current node being processed, begins with target location
            came_from: Dict mapping each node to its predecessor in the optimal path
        
        Returns:
            list: Complete path from agent's starting location to target, ordered start->finish
        """

        completed_path.append(val)

        if val in came_from:
            return self.finish_path(completed_path, came_from[val], came_from)
        else:
            return completed_path[::-1]
        
    
    @abstractmethod
    def find_target(self) -> tuple:
        pass

    # Follows the predefined path, avoiding local obstacles
    def follow_path(self) -> tuple:
        """
        Navigates along the pre-calculated path while avoiding dynamic obstacles using local avoidance.
        
        Attempts to follow the A* path by evaluating neighbours and selecting the neighbour that is the closest to the agent's desired destination.
        
        Returns:
            tuple: World coordinates (y, x) of the agent's next position. Returns current position if no valid moves are available.
                
        Implementation:
            - Pops next waypoint from path and converts to perception coordinates
            - Checks if waypoint is within perception range (3 cells in any direction)
            - If too far off course, triggers full path recalculation
            - Evaluates all 8 adjacent cells for the best alternative move
            - Uses Chebyshev heuristic to stay as close to planned path as possible
            - Defaults to staying in place if completely surrounded
        """
        if len(self.path) <= 0:
            return self.location

        # next step in the path
        desired_loc = self.path.pop(0)
        # translation difference
        translation_difference: tuple = (self.location[0] - 3, self.location[1] - 3) #this agent is at the center of its perception (3,3)
        # find desired cell within perception
        perceived_desired_loc: tuple[int, int] = (desired_loc[0] - translation_difference[0], desired_loc[1] - translation_difference[1])
        distance_to_loc: tuple[int, int] = (perceived_desired_loc[0] - 3, perceived_desired_loc[1] - 3)

        # recalculates path if the agent strays too far from path
        if abs(distance_to_loc[0]) >= 3 or abs(distance_to_loc[1]) >= 3:
            self.path = self.find_path(self.target)
            # next step in the path
            desired_loc = self.path.pop(0)
            # translates the difference from the world grid to the agent's perception grid
            translation_difference: tuple = (self.location[0] - 3, self.location[1] - 3) #this agent is at the center of its perception (3,3)
            # find desired cell within perception
            perceived_desired_loc: tuple[int, int] = (desired_loc[0] - translation_difference[0], desired_loc[1] - translation_difference[1])
            distance_to_loc: tuple[int, int] = (perceived_desired_loc[0] - 3, perceived_desired_loc[1] - 3)

        # list of all neighbours (around center of perception)
        neighbours: list[tuple] = [(2, 2), (2, 3), (2, 4), (3, 2), (4, 2), (3, 4), (4, 4), (4, 3)] 
        best_loc: tuple = (3, 3)  #default (stay in place if there are no new moves)
        best_score: float = math.inf

        # finds best empty cell using Chebyshev's heuristic
        for cell in neighbours:
            heuristic: float = max(abs(perceived_desired_loc[0] - cell[0]), abs(perceived_desired_loc[1] - cell[1]))

            if heuristic < best_score:
                if self.perception[cell[0]][cell[1]].occupant is None and self.perception[cell[0]][cell[1]].is_road: # type: ignore
                    best_loc = cell
                    best_score = heuristic
        
        return (best_loc[0] + translation_difference[0], best_loc[1] + translation_difference[1])


class Civilian(Agent):
    """
    The Civilian class represents individual citizens navigating the urban environment.

    Civilians operate with two independent systems:
    - Behavioral patterns that determine their goals and movement style:
        - Wander: Purposeful movement between target locations along roads
        - Flee: Maximum speed evacuation toward nearest map edge when catastrophe strikes  
        - Safe: Successfully escaped the simulation area
    - Health states that affect their physical capabilities:
        - Healthy: Full movement speed (90% of civilians at start)
        - Sick: Underlying condition, no initial speed penalty (10% at start)
        - Injured: Reduced movement from catastrophe damage
        - Gravely Injured: Critical condition with rapidly deteriorating health
        - Deceased: No longer active in simulation

    Sick civilians are more vulnerable - any injury immediately becomes grave, 
    skipping the regular injured state. All health states affect movement speed.

    Civilians perceive their local environment as a grid centered on their position,
    allowing them to detect nearby agents, obstacles, and potential escape routes.
    """

    #Choices of Civilian Pattern
    class Pattern(Enum):
        WANDER = 1
        FLEE = 2
        SAFE = 3
    
    #Choices of civilian state
    class HealthState(Enum):
        HEALTHY = 1
        SICK = 2
        INJURED = 3
        GRAVELY_INJURED = 4
        DECEASED = 5

    def __init__(self, location: tuple, road_graph: dict):
        self.pattern: Civilian.Pattern = self.Pattern.WANDER
        self.health_state: Civilian.HealthState = self.HealthState.HEALTHY
        self.max_speed: float = 0  # TODO: come up with maximum speed equation. 
        self.road_graph = road_graph
        super().__init__(location, road_graph, self.find_target())

    #updates this civilians position
    def update(self):
        if self.path:
            self.location = self.follow_path()
        else:
            # Reached destination, find new target
            self.target = self.find_target()
            self.path = self.find_path(self.target)

    def find_target(self) -> tuple: # type: ignore
        if self.pattern == self.Pattern.WANDER:
            import random
            road_cells = list(self.road_graph.keys())
            return road_cells[random.randrange(len(road_cells))]
        elif self.pattern == self.Pattern.FLEE:
            # Find nearest edge (implement later)
            pass
        elif self.pattern == self.Pattern.SAFE:
            # Already safe, stay put
            return self.location
        
