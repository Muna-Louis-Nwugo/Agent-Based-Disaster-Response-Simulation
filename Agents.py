import numpy as np
from enum import Enum

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

class Civilian():
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

    def __init__(self, location: tuple, perception: np.ndarray):
        self.location: tuple = location
        self.perception: np.ndarray = perception
        self.pattern: Civilian.Pattern = self.Pattern.WANDER
        self.health_state: Civilian.HealthState = self.HealthState.HEALTHY
        self.max_speed: float = None  # TODO: come up with maximum speed equation. 