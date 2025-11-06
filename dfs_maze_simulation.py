import pygame
import random

pygame.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 800, 600
CELL = 16
ROWS, COLS = HEIGHT // CELL, WIDTH // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DFS Maze Exploration")

# --- Colors ---
ROAD = (70, 70, 70)       # path
WALL = (30, 30, 30)       # wall
CAR = (255, 60, 60)       # moving car
PATH = (0, 255, 0)        # found path
EXPLORED = (255, 200, 0)  # explored cells
BG = (20, 20, 20)
EXIT_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 255)

font = pygame.font.SysFont("arial", 16, bold=True)

# --- Generate maze ---
maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]

def generate_maze():
    stack = []
    start = (1, 1)
    maze[start[1]][start[0]] = 0
    stack.append(start)

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
            nx, ny = x+dx, y+dy
            if 0 < nx < COLS-1 and 0 < ny < ROWS-1 and maze[ny][nx] == 1:
                neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[(y+ny)//2][(x+nx)//2] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

generate_maze()

# --- Fixed reachable exits manually ---
exits = [
    (COLS-2, 1),     # top right
    (COLS-2, ROWS-2) # bottom right
]

# Ensure exits are connected to the maze path
for x, y in exits:
    if maze[y][x] == 1:
        if maze[y+1][x] == 0:
            maze[y][x] = 0
        elif maze[y-1][x] == 0:
            maze[y][x] = 0
        elif maze[y][x+1] == 0:
            maze[y][x] = 0
        elif maze[y][x-1] == 0:
            maze[y][x] = 0

# --- DFS setup ---
dfs_came_from = {}
visited = set()
exploration_sequence = []
stack = []

start = (1, 1)
car_pos = start
final_path = []
car_index = 0
found_exit = False
target_exit = None
dfs_active = False

def reconstruct_path(node):
    path = []
    while node:
        path.append(node)
        node = dfs_came_from[node]
    path.reverse()
    return path

def move_car(path, index):
    if index < len(path):
        return path[index], index+1
    return path[-1], index

# --- Main Loop ---
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL, my // CELL
            if (gx, gy) in exits:
                # Start DFS towards clicked exit
                dfs_came_from = {start: None}
                visited = set([start])
                stack = [start]
                exploration_sequence = []
                car_pos = start
                final_path = []
                car_index = 0
                found_exit = False
                dfs_active = True
                target_exit = (gx, gy)

    # DFS exploration step
    if dfs_active and not found_exit and stack:
        current = stack.pop()
        exploration_sequence.append(current)
        if current == target_exit:
            final_path = reconstruct_path(current)
            found_exit = True
            car_index = 0
        else:
            # move only on grey paths (maze[y][x]==0)
            for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
                nx, ny = current[0]+dx, current[1]+dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx]==0 and (nx,ny) not in visited:
                    visited.add((nx,ny))
                    dfs_came_from[(nx,ny)] = current
                    stack.append((nx,ny))

    # Draw maze
    screen.fill(BG)
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*CELL, y*CELL, CELL-1, CELL-1)
            pygame.draw.rect(screen, ROAD if maze[y][x]==0 else WALL, rect)

    # Draw explored cells
    for ex, ey in exploration_sequence:
        pygame.draw.circle(screen, EXPLORED, (ex*CELL+CELL//2, ey*CELL+CELL//2), 3)

    # Draw DFS path for car
    if found_exit and final_path:
        for px, py in final_path:
            pygame.draw.circle(screen, PATH, (px*CELL+CELL//2, py*CELL+CELL//2), 4)
        car_pos, car_index = move_car(final_path, car_index)

    # Draw car
    pygame.draw.circle(screen, CAR, (car_pos[0]*CELL+CELL//2, car_pos[1]*CELL+CELL//2), 6)

    # Draw exits with labels
    for i, (ex, ey) in enumerate(exits):
        pygame.draw.circle(screen, EXIT_COLOR, (ex*CELL+CELL//2, ey*CELL+CELL//2), 6)
        label = font.render(f"Exit {i+1}", True, TEXT_COLOR)
        screen.blit(label, (ex*CELL+8, ey*CELL+8))

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
