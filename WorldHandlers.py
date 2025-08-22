from WorldEvents import subscribe
import Agents
import random
import numpy as np

"""
WorldHandlers Module - Event response handlers for the Urban Catastrophe Simulation.

This module contains handler functions that respond to system events and modify
simulation state accordingly. It handles:
- Disaster initiation and casualty distribution
- Agent injury state transitions
- Emergency response dispatch coordination
- Dynamic system updates based on event triggers
- Cross-module state modifications

Handler functions receive event data as dictionaries and apply appropriate
changes to the World and Agent states.
"""


def injure_near_disaster(data: dict):

    """
    Applies injury and death states to civilians within the disaster impact zone.
    
    Examines a 7x7 grid centered on the disaster location. Civilians in the 
    immediately adjacent cells (death radius) are killed instantly. Civilians 
    in the outer ring have a 50% chance of normal injury and 50% chance of 
    grave injury, with sick civilians automatically progressing to grave injury
    regardless of roll.
    
    Args:
        data: Dictionary containing:
            - world: World instance with the simulation state
            - disaster_location: Tuple (y, x) coordinates of disaster epicenter
    
    Side Effects:
        - Modifies health_state of affected civilian agents
        - Deaths create permanent obstacles in the grid
    """

    # extract data from dictionary
    world = data["world"]
    location: tuple = data["disaster_location"]

    # slice the map to get the area around the disaster site (disaster should end up at (3, 3))
    area_around_disaster: np.ndarray = world.map[location[0] - 3: location[0] + 4, location[1] - 3: location[1] + 4]

    # all the cells immediately next to the disaster site, any agent in one of these cells will die (RIP)
    death_radius: list[tuple] = [(2, 2), (2, 3), (2, 4), (3, 2), (4, 2), (3, 4), (4, 4), (4, 3), (3, 3)]

    # loop through all the cells surrounding the disaster, killing or injuring agents
    # nested loop to keep track of coordinates
    for i in range(len(area_around_disaster)):
        for j in range(len(area_around_disaster[i])):
            cell = area_around_disaster[i][j]

            # if a cell is a building, skip, cuz we can't kill or injure buildings
            if not cell.is_road:
                continue

            if cell.occupant is not None:
                # defensive redundency check, there should be nothing BUT civilians on the map at this point
                if isinstance(cell.occupant, Agents.Civilian):
                    # kills any civilians inside death radius
                    if (i, j) in death_radius:
                        cell.occupant.set_injury(Agents.Civilian.HealthState.DECEASED)

                    else:
                        chance: float = random.random()

                        # injures half of civilians outside blast radius
                        if chance <= 0.5:
                            cell.occupant.set_injury(Agents.Civilian.HealthState.INJURED)
                        
                        # gravely injures half of civilians outside blast radius
                        else:
                            cell.occupant.set_injury(Agents.Civilian.HealthState.GRAVELY_INJURED)
    


def set_subscribe():
    subscribe("disaster_start", injure_near_disaster)