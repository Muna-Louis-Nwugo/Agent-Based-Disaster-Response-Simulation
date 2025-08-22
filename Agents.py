import numpy as np
from enum import Enum
from typing import Callable
from abc import ABC, abstractmethod
import math
import heapq
import random
import operator


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

    disaster_loc: tuple = None #type: ignore

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
        return []

    
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
        - Flee: Evacuation toward nearest map edge when catastrophe strikes  
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

    Every civilian has an innate knowledge of where the disaster is as soon as one civilian
    encounters it, this knowledge, however, is only activated once a civilian has entered the "Flee" state
    """

    # list of all safe cells on the map (cells at the edge of the map)
    # populated by the first agent that needs it, then simply referenced by all the other ones
    safe_cells: list = []

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
        self.time_to_worsen: float = math.inf
        super().__init__(location, road_graph, self.find_target())

    #updates this civilians position
    def update(self):
        if self.pattern == self.Pattern.SAFE or self.health_state == self.HealthState.DECEASED or self.health_state == self.HealthState.GRAVELY_INJURED:
            return

        self.check_perception()
        self.worsen_health()
        
        # Check if at edge (for fleeing agents)
        if self.pattern == self.Pattern.FLEE:
            if any(self.location[0] == edge[0] and self.location[1] == edge[1] for edge in self.safe_cells):
                self.pattern = self.Pattern.SAFE
                #print("Agent safe")
                return  # Don't move anymore
        
        if self.path:
            self.location = self.follow_path()
        else:
            if self.pattern == self.Pattern.WANDER:
                self.target = self.find_target()
            self.path = self.find_path(self.target)

    def find_target(self) -> tuple: # type: ignore
        """
        Determines the agent's target destination based on their current behavioral pattern.
        
        Returns different targets depending on pattern:
        - WANDER: Random road cell from anywhere on the map
        - FLEE: Nearest edge cell that doesn't require moving toward the disaster.
            Lazily initializes and caches all edge road cells on first flee.
            Filters edges based on agent's position relative to disaster to ensure
            movement is always away from danger. Uses Chebyshev distance for selection.
        - SAFE: Current location (agent has escaped and stays put)
        
        Returns:
            tuple: (y, x) coordinates of the target destination
        """

        road_cells = list(self.road_graph.keys())

        if self.pattern == self.Pattern.WANDER:
            return road_cells[random.randrange(len(road_cells))]
        
        elif self.pattern == self.Pattern.FLEE:
            #check if the self.safe_cells list has been populated, if not, populate is
            if len(self.safe_cells) == 0:

                #keeps track of the largest x and y values (map edges)
                y_size, x_size = (0, 0)
                for cell in road_cells:
                    y, x = cell

                    if y > y_size:
                        y_size = y
                    if x > x_size:
                        x_size = x

                #populates slf.safe_cells with the list of valid edge cells
                # valid edge cells are used by iterating up until y_size and x_size (which are the map edges) and checking if they exist in
                # road_cells

                for i in range(y_size + 1):
                    if (i, x_size) in road_cells:
                        self.safe_cells.append((i, x_size))
                    if (i, 0) in road_cells:
                        self.safe_cells.append((i, 0))
                
                for j in range(x_size + 1):
                    if (y_size, j) in road_cells:
                        self.safe_cells.append((y_size, j))

                    if (0, j) in road_cells:
                        self.safe_cells.append((0, j))
                
            
            """
            The following piece of code finds the safe_cell that is the closest to the civilian that doesn't require moving towards the catastrophe
            to reach. It does this by:

            1. Checking where the agent is relative to the disaster (mathematically)
            2. Filtering all safe cells 
            3. looping through to find the closest safe cell by Chebyshev distance
            """

            # contain signs (<=, >=) that are used to filter out safe cells that will put agent in harm's way
            relative_location_y: Callable[[int, int], bool] = None #type: ignore
            relative_location_x: Callable[[int, int], bool] = None #type: ignore

            # decides which signs to use
            if self.disaster_loc[0] <= self.location[0]:
                relative_location_y = operator.ge
            else:
                relative_location_y = operator.le
            
            if self.disaster_loc[1] <= self.location[1]:
                relative_location_x = operator.ge
            else:
                relative_location_x = operator.le
            
            # filters the indices that are safe to travel towards
            valid_indices = [edge for edge in self.safe_cells if relative_location_y(edge[0], self.location[0]) and relative_location_x(edge[1], self.location[1])]
            

            # uses chebyshev distance to find the closest one
            closest_safe_cell: tuple = self.location
            min_distance: float = math.inf
            for i in valid_indices[0]:
                heuristic: float = max(abs(self.safe_cells[i][0] - self.location[0]), abs(self.safe_cells[i][1] - self.location[1]))
                if  heuristic < min_distance:
                    closest_safe_cell = self.safe_cells[i] #type: ignore
                    min_distance = heuristic
            
            """ print(" ")
            print(f"Agent at {self.location}, disaster at {self.disaster_loc}")
            print(f"Relative: y={relative_location_y}, x={relative_location_x}")
            print(f"Valid edges found: {len(valid_indices[0])}")
            if len(valid_indices[0]) > 0:
                print(f"First few valid edges: {[self.safe_cells[i] for i in valid_indices[0][:5]]}")
            
            print(tuple(closest_safe_cell)) """
            
            return tuple(closest_safe_cell)


        elif self.pattern == self.Pattern.SAFE:
            # Already safe, stay put
            return self.location
        
    #checks perception to modify state
    def check_perception(self) -> None:
        if self.pattern == self.Pattern.WANDER:
            self.check_perception_wander()
        elif self.pattern == self.Pattern.FLEE:
            self.check_perception_flee()
        else:
            return

        
    #checks perception while wandering 
    def check_perception_wander(self) -> None:
        """
        Checks civilian perception to decide whether this civilian should flee

        Rules from the civilian's perspective:
            1. If I'm already fleeing or safe, do not check my perception
            2. If I see a disaster, flee
            3. If I see more than 5 other civilians fleeing, flee

        Side Effects:
            Modifies this civilian's behavioral pattern.
        """

        if self.pattern == self.Pattern.FLEE or self.pattern == self.Pattern.SAFE:
            return  # Already fleeing/safe, don't check again

        num_fleeing_agents = 0

        for cell in self.perception.flatten():
            if isinstance(cell.occupant, Civilian):
                if cell.occupant.pattern == Civilian.Pattern.FLEE:
                    num_fleeing_agents += 1

            if cell.disaster or num_fleeing_agents > 5:
                self.pattern = self.Pattern.FLEE
                self.target = self.find_target()
                self.path = self.find_path(self.target)
                break
    

    # checks perception during fleeing
    def check_perception_flee(self) -> None:
        """
        Gives each agent a chance of getting more severely injured during a crowd scenario

        Method:
            1. counts the number of agents arround
            2. if that number is over 20, 5% chance that the injury worsens
        """
        total_surrounding = sum([
            1 for cell in self.perception.flatten() 
            if cell.occupant is not None
            and cell.occupant != self
            and cell.occupant.health_state != self.HealthState.DECEASED  # Dead people can't trample
            ])

        if total_surrounding >= 20:
            if random.random() <= 0.05:
                self.set_injury(self.HealthState.INJURED)

    
    #sets this civilian to the desired injury level
    def set_injury(self, injury_level: HealthState) -> None:
        """
        Transitions civilian's health state based on injury severity and current condition.
        
        State transition rules:
        - GRAVELY_INJURED civilians always die regardless of new injury
        - Attempting to set DECEASED always results in death
        - HEALTHY civilians set to INJURED become INJURED
        - All other combinations escalate to GRAVELY_INJURED (includes SICK taking any
        injury, INJURED taking another injury, or direct grave injury assignment)
        
        Args:
            injury_level: Target HealthState to apply to the civilian
            
        Side Effects:
            - Updates self.health_state
            - Prints injury status to console
        """

        if injury_level == self.HealthState.DECEASED or self.health_state == self.HealthState.GRAVELY_INJURED:
            self.health_state = self.HealthState.DECEASED
            print("civilian dead.")
        elif injury_level == self.HealthState.INJURED and self.health_state == self.HealthState.HEALTHY:
            self.health_state = self.HealthState.INJURED
            print("civilian injured")
        else: 
            self.health_state = self.HealthState.GRAVELY_INJURED
            print("civilian gravely injured")
    
    
    # worsens health over time after injure   
    def worsen_health(self) -> None:
        """
        Progresses injury states over time, simulating deteriorating health without medical attention.
        
        Injured civilians deteriorate to gravely injured after 60 ticks, then to deceased after 
        20 additional ticks. Uses a countdown timer (time_to_worsen) that initializes to infinity
        when unset, then counts down to zero to trigger state transitions.
        
        State progression:
            INJURED -> (60 ticks) -> GRAVELY_INJURED -> (20 ticks) -> DECEASED
        
        No effect on HEALTHY, SICK, or already DECEASED civilians.
        Must be called each update tick for injured civilians.
        """
        time_to_grave_injury: float = 60
        time_to_death: float = 20

        if self.health_state == self.HealthState.HEALTHY or self.health_state == self.HealthState.SICK or self.health_state == self.HealthState.DECEASED:
            return
        
        elif self.health_state == self.HealthState.INJURED:
            if self.time_to_worsen == math.inf:
                self.time_to_worsen = time_to_grave_injury

            elif self.time_to_worsen == 0:
                self.set_injury(self.HealthState.GRAVELY_INJURED)
                self.time_to_worsen = time_to_death

            else:
                self.time_to_worsen -= 1

        elif self.health_state == self.HealthState.GRAVELY_INJURED:
            if self.time_to_worsen == math.inf:
                self.time_to_worsen = time_to_death

            elif self.time_to_worsen == 0:
                self.set_injury(self.HealthState.DECEASED)

            else:
                self.time_to_worsen -= 1