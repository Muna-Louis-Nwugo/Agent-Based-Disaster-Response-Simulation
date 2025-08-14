# Urban Catastrophe Simulation
#### An agent-based simulation designed to model resource management, first-responder decision making, and civilian behaviour during a catastrophic urban event.

For the past couple of months, I've been swimming in the shallow pools of simulation with my Wildfire Project, which gave me the confidence to try swimming in a small lake. I recently stumbled upon the Agent-based modeling lake on Google Maps, and it gave me the idea to rewind history a bit and ask myself, "What historical event would this kind of simulation have helped prepare for?".

This project was inspired by the 9/11 attacks on New York City. I had originally intended to test different Emergency Response systems and compare things like different communication protocols and centralized vs decentralized control, but I quickly realized that all of that might be just a _little_ outside my capabilities at the moment. So I scaled it back to something more focused: a system that models how first responders are dispatched and make decisions while also discovering interesting emergent behaviours that could occur when you have hundreds or thousands of civilians fleeing a single catastrophe. It's meant to be a general educational resource for anyone interested, though I would love to come back and build that original idea once my skills permit.

---

## System Architecture
I believe that systems should always be architected as if they were going to be extended, and this project is no different. I've developed a modular system that emphasizes extensibility, especially since I plan on returning and improving my project later. 
```
              Render
              ^  |
              |  V
    ---------- World <--- World Handlers
    |            |             ^
    V            V             |
  Agents -> World Events -------
                      
```

### Agents [The Workers]
- Contains agent classes, managing agent goals and behaviours (see Agent Behaviours)
- Agents are passed information about their surroundings from World Module
- Posts agent updates (e.g. injured or unfortunately deceased)

### World [The Environment]
- Contains the World class
- Map that stores Agent objects
- Passes perception data to Agents
- Handles tick-by-tick updates
- Sends information about world state to render
- Posts information about system updates (e.g. catastrophe initiated) to World Events

### World Events [The Messenger]
- Receives system updates from World and Agents, ferries update information to the appropriate World Handlers functions

### World Handlers [The Executioner]
- Updates specific parts of the system based on other system updates (e.g. Civilian injured -> check available paramedics -> dispatch paramedics)

### Render [The Display]
- Sends World Config data from the user to world
- Receives system state updates

Note: Both **Agents** and the **World** can emit events. These are routed through the **World Events** system and processed by the **World Handlers**, which apply the appropriate changes to the simulation state.

---
## Agent Behaviours
Each agent has different states and decision-making patterns to realistically simulate emergency scenarios.

### Civilian
**Patterns: Wander, Flee, Safe**
- Wander: Civilian wanders along roads from target to target on a map, taking into account how people go from one point to the next instead of aimlessly meandering
- Flee: Civilian establishes an exit (point on the edge of the map, preferably the closest, but not always) and flees towards that point at the maximum possible speed
- Safe: Civilian has successfully escaped

**States: Healthy, Sick, Injured, Gravely Injured, Deceased**
- Healthy: The civilian has no injuries (90% of civilians at the start)
- Sick: Civilian has an underlying condition (10% of civilians at the start)
  - Makes any sustained injures more severe
- Injured: Civilian that has been injured during catastrophe
- Gravely Injured: Second stage of injury, civilian's condition deteriorates rapidly
- Deceased: Civilian has died (RIP)

##### Civilian states affects maximum civilian speed

### Paramedic
**Patterns: Civilian Priority, Catastrophe Priority**
- Civilian Priority: Paramedic focuses on tending to injured civilian target before heading to catastrophe zone
- Catastrophe Priority: Paramedic rushes to catastrophe site, regardless of injured civilians on the way
###### Note: I'm debating whether to have paramedics assigned to a pattern, or dynamically decide on a pattern based on the environmnent. I shall test these two strategies.

**States: Standby, Dispatched**
- Standby: Paramedic is at starting location (hospital / ambulance center)
- Dispatched: Paramedic is responding to an injury

### Firefighters
**Patterns: Engage**
- Engage: Head directly to catastrophe site

**States: Standby, Dispatched**
- Standby: Firefighter at fire station
- Dispatched: Firefighter en route to catastrophe site

Police Agents proved to require a lot of complexity to be even remotely accurate (perimeter establishment, crowd control, etc.), so I've decided to skip them and try tackle them with the next iteration of this project.

---
## Technologies/Methods Used
### Planned
- Python
- Numpy
- Agent-Based Modeling
- Pathfinding Algorithms
- Multi-Agent Coordination
- Object Oriented Programming
- Event Driven Architecture
- PyGame

---
## Project Status
### Completed
- Cevilian scaffolding
- General Agent spawn
- General Agent awareness
- Agent Pathfinding
- Agent pathfollowing and local avoidance


### In Progress
- Agent destination decisions
- Proper Agent movement at intersection

### Planned
- Advanced agent pathfinding and reactions to surroudings(Repath Penalty)
- Paramedic scaffolding
- Firefighter scaffolding

