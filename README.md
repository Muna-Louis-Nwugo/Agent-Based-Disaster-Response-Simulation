# Urban Catastrophe Simulation
#### An agent-based simulation designed to model resource management, first-responder decision making, and civilian behaviour during a catastrophic urban event.

For the past couple of months, I've been swimming in the shallow pools of simulation with my Wildfire Project, which gave me the confidence to try swimming in a small lake. I recently stumbled upon the Agent-based modeling lake on Google Maps, and it gave me the idea to rewind history a bit and ask myself, "What historical event would this kind of simulation have helped prepare for?".

This project was inspired by the 9/11 attacks on New York City. I had originally intended to test different Emergency Response systems and compare things like different communication protocols and centralized vs decentralized control, but I quickly realized that all of that might be just a _little_ outside my capabilities at the moment. So I scaled it back to something more focused: a system that models how first responders are dispatched and make decisions while also discovering interesting emergent behaviours that could occur when you have hundreds or thousands of civilians fleeing a single catastrophe. It's meant to be a general educational resource for anyone interested, though I would love to come back and build that original idea once my skills permit.

---

## System Architecture

```
Render ←→ World ←→ Agents
            ↓
        World Events
            ↓
    World Event Handlers
```
