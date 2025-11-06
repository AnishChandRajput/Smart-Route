import pygame
import random
from collections import deque

pygame.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 800, 600
CELL = 20
ROWS, COLS = HEIGHT // CELL, WIDTH // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI City Map - Blind Search Simulation")

# --- Colors ---
ROAD = (70, 70, 70)
HOUSE = (140, 120, 100)
HOSPITAL = (200, 70, 70)
SCHOOL = (70, 140, 200)
PARK = (70, 170, 70)
CAR = (255, 60, 60)
PATH = (0, 255, 0)
EXPLORED = (255, 200, 0)
BG = (25, 25, 25)
GOAL_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (255, 215, 0)
TEXT_COLOR = (255, 255, 255)

font = pygame.font.SysFont("arial", 14, bold=True)

# --- Generate base grid ---
city_map = []
for y in range(ROWS):
    row = []
    for x in range(COLS):
        if x % 4 == 0 or y % 5 == 0:
            row.append(0)  # road
        else:
            row.append(1)  # empty land/building
    city_map.append(row)

# --- Mark buildings ---
def fill_area(x1, y1, x2, y2, code):
    for yy in range(y1, y2):
        for xx in range(x1, x2):
            if 0 <= xx < COLS and 0 <= yy < ROWS:
                city_map[yy][xx] = code

fill_area(2, 2, 8, 8, 3)  # Houses
fill_area(2, ROWS - 10, 10, ROWS - 3, 4)  # School
fill_area(COLS - 10, 3, COLS - 3, 10, 5)  # Hospital
fill_area(COLS // 2 - 5, ROWS // 2 - 3, COLS // 2 + 5, ROWS // 2 + 3, 6)  # Park

# --- Add random obstacles ---
obstacles = []
for _ in range(20):
    x = random.randint(0, COLS - 1)
    y = random.randint(0, ROWS - 1)
    if city_map[y][x] == 0 and (x, y) != (1, 1):
        city_map[y][x] = 2
        obstacles.append((x, y))

# --- BFS containers ---
bfs_came_from = {}

def blind_search_stepwise(start, goal):
    global bfs_came_from
    bfs_came_from = {}

    if city_map[goal[1]][goal[0]] != 0:
        yield "invalid", []
        return

    q = deque([start])
    bfs_came_from[start] = None
    explored = []
    visited = set([start])

    while q:
        cur = q.popleft()
        explored.append(cur)
        yield cur, list(explored)

        if cur == goal:
            break

        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # up,right,down,left
            nx, ny = cur[0] + dx, cur[1] + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if (nx, ny) not in visited and city_map[ny][nx] == 0:
                    visited.add((nx, ny))
                    bfs_came_from[(nx, ny)] = cur
                    q.append((nx, ny))

    yield None, list(explored)
    return

def reconstruct_path(goal):
    path = []
    node = goal
    while node is not None and node in bfs_came_from:
        path.append(node)
        node = bfs_came_from[node]
    path.reverse()
    return path

# --- Car Setup ---
start = (1, 1)
goal = (COLS - 3, ROWS - 3)
search_generator = blind_search_stepwise(start, goal)
exploration_sequence = []
car_cell_index = 0
car_pos = start
final_path = []
following_final_path = False

# --- Move car one cell per frame ---
def move_car_cell(car_cell_index, path):
    if car_cell_index < len(path):
        return path[car_cell_index], car_cell_index + 1
    return path[-1], car_cell_index

# --- Main Loop ---
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL, my // CELL
            if 0 <= gx < COLS and 0 <= gy < ROWS and city_map[gy][gx] == 0:
                start_cell = car_pos
                goal = (gx, gy)
                search_generator = blind_search_stepwise(start_cell, goal)
                exploration_sequence = []
                final_path = []
                following_final_path = False
                car_cell_index = 0

    # BFS step
    try:
        step, explored_cells = next(search_generator)
        if step == "invalid":
            explored_cells = []
        elif step is None:
            if goal in bfs_came_from:
                final_path = reconstruct_path(goal)
                following_final_path = True
                car_cell_index = 0
        else:
            exploration_sequence.append(step)
    except StopIteration:
        pass

    # Draw map
    screen.fill(BG)
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL, y * CELL, CELL - 1, CELL - 1)
            cell = city_map[y][x]
            if cell == 0:
                pygame.draw.rect(screen, ROAD, rect)
            elif cell == 1:
                pygame.draw.rect(screen, (100, 100, 120), rect)
            elif cell == 2:
                pygame.draw.rect(screen, ROAD, rect)
                pygame.draw.circle(screen, OBSTACLE_COLOR, (x * CELL + CELL // 2, y * CELL + CELL // 2), 5)
            elif cell == 3:
                pygame.draw.rect(screen, HOUSE, rect)
            elif cell == 4:
                pygame.draw.rect(screen, SCHOOL, rect)
            elif cell == 5:
                pygame.draw.rect(screen, HOSPITAL, rect)
            elif cell == 6:
                pygame.draw.rect(screen, PARK, rect)

    # Draw explored cells
    for ex, ey in exploration_sequence:
        pygame.draw.circle(screen, EXPLORED, (ex * CELL + CELL // 2, ey * CELL + CELL // 2), 3)

    # Draw final path
    if following_final_path:
        for px, py in final_path:
            pygame.draw.circle(screen, PATH, (px * CELL + CELL // 2, py * CELL + CELL // 2), 4)

    # --- Move car ONLY if BFS finished ---
    if following_final_path and final_path:
        car_pos, car_cell_index = move_car_cell(car_cell_index, final_path)
        if car_cell_index >= len(final_path):
            following_final_path = False
            exploration_sequence = []
            car_cell_index = 0
    # else: car stays at current cell until BFS finishes

    # Draw car
    pygame.draw.circle(screen, CAR, (car_pos[0] * CELL + CELL // 2, car_pos[1] * CELL + CELL // 2), 8)
    pygame.draw.circle(screen, GOAL_COLOR, (goal[0] * CELL + CELL // 2, goal[1] * CELL + CELL // 2), 5)

    # Labels
    screen.blit(font.render("HOSPITAL", True, TEXT_COLOR), (WIDTH - 170, 40))
    screen.blit(font.render("SCHOOL", True, TEXT_COLOR), (50, HEIGHT - 120))
    screen.blit(font.render("PARK", True, TEXT_COLOR), (WIDTH // 2 - 40, HEIGHT // 2 - 20))
    screen.blit(font.render("HOUSE", True, TEXT_COLOR), (100, 60))

    pygame.display.flip()
    clock.tick(10)  # slow for visualization

pygame.quit()
