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
      ------ World ----------
      |                     |
      V                     V 
   Agents------------> World Events 
                             |
                             V
                        World Handlers
```

### Agents [The Workers]
- Contains agent classes, managing agent goals and behaviours
- Agents are passed information about their surroundings from World Module
- Posts agent updates (e.g. injured or unfortunately deceased)

### World [The Environment]
- Contains the World class
- Passes perception data to Agents
- Handles tick-by-tick updates
- Sends information about world state to render
- Posts information about system updates (e.g. catastrophe initiated) to World Events

### World Events [The Messenger]
- Receives system updates from World and Agents, ferries update information to the appropriate World Handlers functions

### World Handlers [The Executioner]
- Updates specific parts of the system based on other system updates (e.g. Civilian injured -> check available ambulances -> dispatch ambulances)

### Render [The Display]
- Sends World Config data from the user to world
- Receives system state updates

Note: Both **Agents** and the **World** can emit events. These are routed through the **World Events** system and processed by the **World Handlers**, which apply the appropriate changes to the simulation state.

---
## Agent Behaviours
