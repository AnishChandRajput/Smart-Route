import pygame
import heapq
import math
import random

pygame.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 800, 600
CELL = 20
ROWS, COLS = HEIGHT // CELL, WIDTH // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI City Map Path-Finding Simulation")

# --- Colors ---
ROAD = (70, 70, 70)
HOUSE = (140, 120, 100)
HOSPITAL = (200, 70, 70)
SCHOOL = (70, 140, 200)
PARK = (70, 170, 70)
CAR = (255, 60, 60)
PATH = (0, 255, 0)
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
            row.append(1)  # empty land/building placeholder
    city_map.append(row)

# --- Mark specific building areas ---
def fill_area(x1, y1, x2, y2, code):
    for y in range(y1, y2):
        for x in range(x1, x2):
            if 0 <= x < COLS and 0 <= y < ROWS:
                city_map[y][x] = code

# Houses block (top-left area)
fill_area(2, 2, 8, 8, 3)

# School area (bottom-left)
fill_area(2, ROWS - 10, 10, ROWS - 3, 4)

# Hospital area (top-right)
fill_area(COLS - 10, 3, COLS - 3, 10, 5)

# Park (center region)
fill_area(COLS // 2 - 5, ROWS // 2 - 3, COLS // 2 + 5, ROWS // 2 + 3, 6)

# --- Add random obstacles (roadblocks) ---
obstacles = []
for _ in range(30):
    x = random.randint(0, COLS - 1)
    y = random.randint(0, ROWS - 1)
    if city_map[y][x] == 0:
        city_map[y][x] = 2
        obstacles.append((x, y))

# --- A* Pathfinding ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal):
    if city_map[goal[1]][goal[0]] not in [0]:
        return []
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {}
    cost_so_far = {start: 0}
    came_from[start] = None
    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = current[0]+dx, current[1]+dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if city_map[ny][nx] != 0:
                    continue
                new_cost = cost_so_far[current] + 1
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + heuristic(goal, (nx, ny))
                    heapq.heappush(queue, (priority, (nx, ny)))
                    came_from[(nx, ny)] = current
    path = []
    node = goal
    while node and node in came_from:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path

# --- Car Setup ---
start = (1, 1)
goal = (COLS - 3, ROWS - 3)
path = astar(start, goal)
car_x, car_y = start[0]*CELL + CELL//2, start[1]*CELL + CELL//2
path_index = 0
car_speed = 2

# --- Main Loop ---
clock = pygame.time.Clock()
running = True
goal_set = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL, my // CELL
            if city_map[gy][gx] == 0:
                goal = (gx, gy)
                path = astar((int(car_x // CELL), int(car_y // CELL)), goal)
                path_index = 0
                goal_set = True

    screen.fill(BG)

    # Draw map
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*CELL, y*CELL, CELL-1, CELL-1)
            cell = city_map[y][x]
            if cell == 0:
                pygame.draw.rect(screen, ROAD, rect)
            elif cell == 1:
                pygame.draw.rect(screen, (100, 100, 120), rect)
            elif cell == 2:
                pygame.draw.rect(screen, ROAD, rect)
                pygame.draw.circle(screen, OBSTACLE_COLOR, (x*CELL+CELL//2, y*CELL+CELL//2), 5)
            elif cell == 3:
                pygame.draw.rect(screen, HOUSE, rect)
            elif cell == 4:
                pygame.draw.rect(screen, SCHOOL, rect)
            elif cell == 5:
                pygame.draw.rect(screen, HOSPITAL, rect)
            elif cell == 6:
                pygame.draw.rect(screen, PARK, rect)

    # Labels for big areas
    screen.blit(font.render("HOSPITAL", True, TEXT_COLOR), (WIDTH - 170, 40))
    screen.blit(font.render("SCHOOL", True, TEXT_COLOR), (50, HEIGHT - 120))
    screen.blit(font.render("PARK", True, TEXT_COLOR), (WIDTH//2 - 40, HEIGHT//2 - 20))
    screen.blit(font.render("HOUSE", True, TEXT_COLOR), (100, 60))

    # Draw path
    if goal_set:
        for (px, py) in path:
            pygame.draw.circle(screen, PATH, (px*CELL+CELL//2, py*CELL+CELL//2), 3)

    # Move car smoothly
    if path_index < len(path):
        target = path[path_index]
        tx, ty = target[0]*CELL + CELL//2, target[1]*CELL + CELL//2
        dx, dy = tx - car_x, ty - car_y
        dist = math.hypot(dx, dy)
        if dist < 2:
            path_index += 1
        else:
            car_x += (dx/dist)*car_speed
            car_y += (dy/dist)*car_speed

    # Draw car and goal
    pygame.draw.circle(screen, CAR, (int(car_x), int(car_y)), 8)
    if goal_set:
        pygame.draw.circle(screen, GOAL_COLOR, (goal[0]*CELL + CELL//2, goal[1]*CELL + CELL//2), 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
