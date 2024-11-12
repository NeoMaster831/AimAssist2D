# v2.1

import numpy as np

# x, y, x_t, y_t are all "real" positions
def F(x, y, x_t, y_t, V=160.0, sigma=51.9, k=0.5): # sigma ~= V / 3
    
    D = np.sqrt((x - x_t)**2 + (y - y_t)**2)
    G = np.exp(-((x - x_t)**2 + (y - y_t)**2) / (2 * sigma**2)) # Gaussian function
    
    delta_x, delta_y = 0, 0
    
    if D <= V:
        delta_x = (x_t - x) * k * G
        delta_y = (y_t - y) * k * G
    
    return x + delta_x, y + delta_y, delta_x, delta_y

class AimAssistV2p1:
    def __init__(self):
        self.V = 160.0
        self.sigma = 51.9
        self.k = 0.5

        # Real position, that means the "real" position if the assist is not occured.
        self.real_position = self.get_position()
        
        # The last position corresponds to the real position.
        self.last_position = self.real_position
    
    def get_position(self):
        pass

    def set_position(self, x, y):
        pass

    def update(self, target_position):
        
        if self.last_position != self.get_position():
            
            dx, dy = self.get_position() - self.last_position

            # TODO: add exception handling
            self.real_position[0] += dx
            self.real_position[1] += dy

            cx, cy, _, _ = F(self.real_position[0], self.real_position[1], target_position[0], target_position[1])

            self.set_position(cx, cy)
            self.last_position = cx, cy
    
    # The delta is 'not' occured, so we change the force before the change occurs
    def update_as_delta(self, dx, dy, target_position):
        if dx == 0 and dy == 0:
            return
        
        self.real_position[0] += dx
        self.real_position[1] += dy

        cx, cy, _, _ = F(self.real_position[0], self.real_position[1], target_position[0], target_position[1])

        self.set_position(cx, cy)
        self.last_position = cx, cy


import matplotlib.pyplot as plt

def Visualize_F():
    x = np.linspace(0, 1920, 60)
    y = np.linspace(0, 1080, 40)
    X, Y = np.meshgrid(x, y)

    # Calculate new positions
    X_new = np.zeros_like(X)
    Y_new = np.zeros_like(Y)

    for i in range(40):
        for j in range(60):
            X_new[i,j], Y_new[i,j], _, _ = F(X[i,j], Y[i,j], 720, 500)

    plt.figure(figsize=(19.2, 10.8))
    plt.scatter(X_new, Y_new, c='blue', label='Points')
    plt.scatter(X, Y, c='red', label='Points')

    circle = plt.Circle((720, 500), 160.0, fill=False, color='green', linestyle='--', label='V radius')
    plt.gca().add_patch(circle)

    plt.plot(720, 500, 'r*', markersize=15, label='Target')
    plt.grid(True)
    plt.legend()
    plt.title('Force Field Visualization')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

Visualize_F()