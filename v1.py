# v1

import pygame
import math

PYGAME_MITIGATION = 1.5

def dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def check_angle(A, B, C, threshold):
    ABx = B[0] - A[0]
    ABy = B[1] - A[1]
    ACx = C[0] - A[0]
    ACy = C[1] - A[1]
    
    # Dot product of vectors AB and AC
    dot_product = ABx * ACx + ABy * ACy
    
    # Magnitudes of vectors AB and AC
    magnitude_AB = math.hypot(ABx, ABy)
    magnitude_AC = math.hypot(ACx, ACy)
    
    # Avoid division by zero
    if magnitude_AB == 0 or magnitude_AC == 0:
        print("One of the vectors has zero length.")
        return False
    
    # Compute cosine of the angle between AB and AC
    cos_theta = dot_product / (magnitude_AB * magnitude_AC)
    
    # Clamp the cosine value to the valid range [-1, 1]
    cos_theta = max(-1, min(1, cos_theta))
    
    # Compute the angle in degrees
    theta_rad = math.acos(cos_theta)
    theta_deg = math.degrees(theta_rad)
    
    # Get the acute angle between the lines
    if theta_deg > 90:
        theta_deg = 180 - theta_deg
    
    print(theta_deg)

    # Check if the angle is approximately 23.2 degrees
    if theta_deg < threshold:
        return True
    else:
        return False

class AimAssist:
    def __init__(self, surface):
        self.active = False
        self.surface = surface
        self.original_mouse_pos = pygame.mouse.get_pos()
        self.debug_info = {
            'original_pos': None,
            'current_pos': None,
            'target_pos': None,
            'adjustment_made': None,  # 'pullback' or 'boost' or None
        }
        self.T = 200
        self.R = 1.05 # Pullback
        self.S = 0.5 # Boost
        self.Z = 45
        self.Z_exit = (False, False) # Triggered, Exit
        self.theta = 23.2
    
    def reset_Z(self):
        self.Z_exit = (False, False)

    def update(self, target_pos, next_target_pos):
        if not target_pos:
            return
            
        dx, dy = pygame.mouse.get_rel()
        if dx == 0 and dy == 0:
            return
        
        current_pos = pygame.mouse.get_pos()
        original_pos = (current_pos[0] - dx, current_pos[1] - dy)

        # Store debug info
        self.debug_info['original_pos'] = original_pos
        self.debug_info['current_pos'] = current_pos
        self.debug_info['target_pos'] = target_pos
        
        if dist(current_pos, target_pos) < self.Z and not self.Z_exit[0]:
            self.Z_exit = (True, False)
        elif dist(current_pos, target_pos) > self.Z and self.Z_exit[0]:
            self.Z_exit = (True, True)

        if dist(original_pos, target_pos) > self.T:
            self.debug_info['adjustment_made'] = None
            return
        
        # Adjust Percentage
        percentage_0 = (dist(original_pos, target_pos) / self.T) * self.R * 0.5
        percentage_1 = (dist(original_pos, target_pos) / self.T) * self.S * 0.5

        next_target_mitigation = 1
        if next_target_pos and self.Z_exit[1] and check_angle(current_pos, original_pos, next_target_pos, self.theta):
            next_target_mitigation = 1.25

        if dist(original_pos, target_pos) < dist(current_pos, target_pos):
            pygame.mouse.set_pos(original_pos[0] + dx * (self.R * 0.5 + percentage_0) * PYGAME_MITIGATION * next_target_mitigation,
                                 original_pos[1] + dy * (self.R * 0.5 + percentage_0) * PYGAME_MITIGATION * next_target_mitigation)
            #pygame.mouse.set_pos(original_pos[0] + dx * PYGAME_MITIGATION, original_pos[1] + dy * PYGAME_MITIGATION)
            self.debug_info['adjustment_made'] = 'pullback'
        else:
            pygame.mouse.set_pos(current_pos[0] + dx * (self.S * 0.5 + percentage_1) * PYGAME_MITIGATION * next_target_mitigation,
                                 current_pos[1] + dy * (self.S * 0.5 + percentage_1) * PYGAME_MITIGATION * next_target_mitigation)
            #pygame.mouse.set_pos(original_pos[0] + dx * PYGAME_MITIGATION, original_pos[1] + dy * PYGAME_MITIGATION)
            self.debug_info['adjustment_made'] = 'boost'

    def draw_debug(self):
        if not all(self.debug_info.values()):
            return

        # Colors
        BLUE = (0, 150, 255)
        RED = (255, 50, 50)
        GREEN = (50, 255, 50)
        PURPLE = (255, 0, 255)
        WHITE = (255, 255, 255)
        
        orig = self.debug_info['original_pos']
        curr = self.debug_info['current_pos']
        target = self.debug_info['target_pos']
        
        # Draw threshold circle around target
        pygame.draw.circle(self.surface, WHITE, target, self.T, 1)
        pygame.draw.circle(self.surface, WHITE, target, self.Z, 1)

        # Draw points
        pygame.draw.circle(self.surface, BLUE, orig, 4)  # Original position
        pygame.draw.circle(self.surface, RED, curr, 4)   # Current position
        
        # Draw movement vector
        pygame.draw.line(self.surface, GREEN, orig, curr, 2)
        
        # Draw target vector
        pygame.draw.line(self.surface, PURPLE, curr, target, 1)
        
        # Draw adjustment indicator
        if self.debug_info['adjustment_made']:
            text = pygame.font.Font(None, 24).render(
                self.debug_info['adjustment_made'].upper(), 
                True, 
                RED if self.debug_info['adjustment_made'] == 'pullback' else GREEN
            )
            self.surface.blit(text, (curr[0] + 10, curr[1] + 10))
