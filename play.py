import pygame
import random
import time
import numpy as np
from collections import deque
from v2 import AimAssist
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
YELLOW = (255, 200, 0)
GREEN = (0, 255, 0)
CIRCLE_RADIUS = 40
NUM_CIRCLES = 4
CROSSHAIR_SIZE = 20
MARGIN = 30

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aim Trainer")
clock = pygame.time.Clock()

# Initialize font
font = pygame.font.Font(None, 36)

# Hide the default cursor
pygame.mouse.set_visible(False)

class Crosshair:
    def __init__(self):
        self.size = CROSSHAIR_SIZE
    
    def draw(self, surface):
        x, y = pygame.mouse.get_pos()
        pygame.draw.circle(surface, GREEN, (x, y), 10)

class Circle:
    def __init__(self):
        self.respawn()
        self.active = True
        self.spawn_time = time.time()
        
    def respawn(self):
        self.x = random.randint(MARGIN + CIRCLE_RADIUS, SCREEN_WIDTH - MARGIN - CIRCLE_RADIUS)
        self.y = random.randint(MARGIN + CIRCLE_RADIUS, SCREEN_HEIGHT - MARGIN - CIRCLE_RADIUS)
        self.spawn_time = time.time()
        
    def draw(self, surface, order):
        if self.active:
            alpha = 255 >> order
            circle_surface = pygame.Surface((CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*YELLOW, alpha), (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)
            surface.blit(circle_surface, (self.x - CIRCLE_RADIUS, self.y - CIRCLE_RADIUS))
    
    def check_click(self, pos):
        if not self.active:
            return False
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        return distance <= CIRCLE_RADIUS

    def draw_line_to_next(self, surface, next_circle, order):
        if self.active and next_circle.active:
            alpha = 255 >> order
            line_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(line_surface, (*YELLOW, alpha), 
                           (self.x, self.y), 
                           (next_circle.x, next_circle.y), 2)
            surface.blit(line_surface, (0, 0))

# Initialize circles queue
circles = deque([Circle() for _ in range(NUM_CIRCLES)])
crosshair = Crosshair()
last_click_time = time.time()
time_taken = 0

# Game loop
running = True
aim_assist = AimAssist(1.0)
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        click_occurred = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_occurred = True
            pos = pygame.mouse.get_pos()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_s, pygame.K_d):
                click_occurred = True
                pos = pygame.mouse.get_pos()
        
        if click_occurred and circles:
            current_circle = circles[0]
            if current_circle.check_click(pos):

                time_taken = time.time() - last_click_time
                last_click_time = time.time()
                
                circles.popleft()
                if circles:
                    next_circle = Circle()
                    circles.append(next_circle)

    # Draw time text
    time_text = font.render(f"Time to click: {time_taken:.3f}s", True, WHITE)
    screen.blit(time_text, (10, 10))

    if len(circles) > 1:
        circles[0].draw_line_to_next(screen, circles[1], 0)
    
    # Then draw circles
    for i, circle in enumerate(circles):
        circle.draw(screen, i)
    
    crosshair.draw(screen)

    # Get current target position if circles exist
    target_pos = (circles[0].x, circles[0].y) if circles else None

    # Update and draw aim assist
    rel = pygame.mouse.get_rel()
    cur_pos = pygame.mouse.get_pos()
    if rel[0] != 0 or rel[1] != 0:
        fx, fy = aim_assist.get_fx_fy(cur_pos, target_pos)
        pygame.mouse.set_pos(cur_pos + np.array([fx, fy]))

    pygame.display.flip()
    clock.tick(10000)

pygame.quit()
