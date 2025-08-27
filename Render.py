import pygame
import sys
import numpy as np
from World import World, Cell
import Agents
import time

# Quick and dirty pygame viewer for debugging
pygame.init()

# Config - matching World.py exactly
CELL_SIZE = 12  # Bigger cells for better visibility
GRID_SIZE = 60  # Same as World.py
FPS = 15  # Adjust this: 5=slow, 15=smooth, 30=fast

# Colors
BLACK = (20, 20, 20)
GRAY = (80, 80, 80)
WHITE = (200, 200, 200)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
BLUE = (0, 100, 255)
ORANGE = (255, 140, 0)
PURPLE = (128, 0, 128)

# Generate EXACT same test city grid as World.py
size = 60
test_grid = [[False for _ in range(size)] for _ in range(size)]

# Create main avenues (3 lanes wide) every 10 blocks
for i in range(0, size, 10):
    for j in range(size):
        # Vertical avenues
        if i < size - 2:
            test_grid[j][i] = True
            test_grid[j][i+1] = True
            test_grid[j][i+2] = True
        # Horizontal avenues
        if j < size - 2:
            test_grid[i][j] = True
            test_grid[i+1][j] = True
            test_grid[i+2][j] = True

# Add smaller streets (2 lanes wide) between avenues
for i in range(5, size, 10):
    for j in range(size):
        # Vertical streets
        if i < size - 1:
            test_grid[j][i] = True
            test_grid[j][i+1] = True
        # Horizontal streets
        if j < size - 1:
            test_grid[i][j] = True
            test_grid[i+1][j] = True

# Convert to numpy array of Cell objects
map_array = np.empty((size, size), dtype=object)
for y in range(size):
    for x in range(size):
        map_array[y, x] = Cell(test_grid[y][x])

# Create world - EXACT same parameters as World.py
world = World(num_civilians=450, num_paramedics=5, map=map_array)

# Pygame setup
screen = pygame.display.set_mode((size * CELL_SIZE, size * CELL_SIZE))
pygame.display.set_caption("Catastrophe Simulation Debug")
clock = pygame.time.Clock()

# Simulation state
running = True
paused = False
disaster_started = False
tick_count = 0
update_time = 0

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
    
    if not paused:
        start = time.time()
        world.update()
        update_time = time.time() - start
        tick_count += 1
        
        # Start disaster at tick 300 like in World.py
        if tick_count == 300 and not disaster_started:
            world.set_disaster_loc((29, 25))  # Same location as World.py
            disaster_started = True
            print("CATASTROPHE COMMENCED")
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw world
    for y in range(size):
        for x in range(size):
            cell = world.map[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Draw base (road vs building)
            if cell.disaster:
                pygame.draw.rect(screen, ORANGE, rect)
            elif not cell.is_road:
                pygame.draw.rect(screen, GRAY, rect)
            else:
                pygame.draw.rect(screen, BLACK, rect)
                
            # Draw occupant
            if cell.occupant:
                occupant_rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, 
                                           CELL_SIZE - 4, CELL_SIZE - 4)
                
                if isinstance(cell.occupant, Agents.Paramedic):
                    pygame.draw.rect(screen, BLUE, occupant_rect)
                elif isinstance(cell.occupant, Agents.Civilian):
                    if cell.occupant.health_state == Agents.Civilian.HealthState.HEALTHY:
                        color = GREEN
                    elif cell.occupant.health_state == Agents.Civilian.HealthState.SICK:
                        color = PURPLE
                    elif cell.occupant.health_state == Agents.Civilian.HealthState.INJURED:
                        color = YELLOW
                    elif cell.occupant.health_state == Agents.Civilian.HealthState.GRAVELY_INJURED:
                        color = RED
                    elif cell.occupant.health_state == Agents.Civilian.HealthState.DECEASED:
                        color = DARK_RED
                    else:
                        color = WHITE
                    
                    pygame.draw.rect(screen, color, occupant_rect)
    
    # Draw stats
    font = pygame.font.Font(None, 24)
    stats = [
        f"Tick: {tick_count}",
        f"FPS: {clock.get_fps():.1f}" if not paused else "PAUSED",
        f"Update: {update_time:.3f}s",
        f"SPACE to pause/unpause",
        f"Disaster at tick 300" if not disaster_started else f"DISASTER ACTIVE"
    ]
    for i, stat in enumerate(stats):
        text = font.render(stat, True, WHITE)
        screen.blit(text, (5, 5 + i * 25))
    
    pygame.display.flip()
    clock.tick(FPS)  # Controlled frame rate for smooth viewing

pygame.quit()
sys.exit()