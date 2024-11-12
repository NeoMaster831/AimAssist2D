# v2.1

from cubic import MonotoneCubic
import numpy as np
import time

def dist(xd, yd):
    return np.sqrt(xd**2 + yd**2)

def dist_between(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# x, y, x_t, y_t are all "real" positions
def gaussian_filter(x, y, x_t, y_t, V=160.0, sigma=51.9, k=0.5): # sigma ~= V / 3, k is the strength of the force
    
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

        self.framerate = 1 / 1000 / 2 # Polling rate * 2 (2000Hz)

        # TODO: change these values (tuning)
        
        # Cubics
        self.distance_cubic = MonotoneCubic(175, 250, 0.5, 5.0, 0.5, 500)
        self.time_cubic = MonotoneCubic(350, 500, 0.35, 2.0, 0.1, 600)

        # Reversed cubics
        self.speed_cubic = MonotoneCubic(150, 350, 1, 3, 1, 500, reversed=True)
        
        self.debt_paying_speed = 0.02 # multiplier (2%)

        self.time_limit = 2.0 # (seconds)
        self.distance_limit = 2000 # (pixels)
        self.speed_limit = 20 # (pixels/frame)

        self.slider_k = 0.7 # multiplier (70% than normal)

        self.reset()
    
    def reset(self):

        # Real position, that means the "real" position if the assist is not occured.
        self.real_position = self.get_position()
        
        # The last position corresponds to the real position.
        self.last_position = self.real_position

        # The 'error' is vector between last position and real position.
        # We define 'debt' as unrecoverable 'error'.
        self.debt = 0, 0
        self.debt_uptime = 0.0 # (seconds)
        self.debt_last_update_time = None

        self.target_position = None
        self.target_time = None

        self.last_target_position = None
        self.last_target_time = None

        self.slider_enabled = False

    def get_position(self):
        pass

    def set_position(self, x, y):
        pass
    
    def get_target_position(self):
        return self.target_position
    
    def set_target_position(self, x, y, is_slider_frame=False):

        if self.target_position == (x, y) or self.target_time == time.time():
            return
        
        # Update new debt, dt
        self.debt = self.real_position[0] - self.last_position[0], self.real_position[1] - self.last_position[1]
        self.debt_uptime = 0
        self.debt_last_update_time = time.time()

        self.last_target_position = self.target_position
        self.last_target_time = self.target_time

        self.target_position = x, y
        self.target_time = time.time()

        self.slider_enabled = is_slider_frame

    # Calculate the mitigation by delta, and error; the vector between last position and real position
    # Returns the mitigated delta
    def mitigate_error(self):
        
        if self.target_position == None or self.last_target_position == None or abs(dist(*self.debt)) < 1:
            return 0, 0
        
        self.debt_uptime += time.time() - self.debt_last_update_time
        self.debt_last_update_time = time.time()

        if self.slider_enabled:
            
            # We see only speed.
            speed = dist_between(self.target_position[0], self.target_position[1], self.last_target_position[0], self.last_target_position[1]) / abs(self.target_time - self.last_target_time)
            if speed > self.speed_limit:
                speed = self.speed_limit

            # Calculate the force
            ratio = self.speed_cubic.F_as_ratio(speed / self.speed_limit * 500)
            ratio *= self.debt_paying_speed

            # Calculate the delta
            dx, dy = ratio * self.debt[0], ratio * self.debt[1]

            return dx, dy

        else:

            # Calculate the force
            distance = dist_between(self.target_position[0], self.target_position[1], self.last_target_position[0], self.last_target_position[1])
            if distance > self.distance_limit:
                distance = self.distance_limit

            ratio = self.distance_cubic.F_as_ratio(distance / self.distance_limit * 500)

            time = self.debt_uptime
            if time > self.time_limit:
                time = self.time_limit

            ratio *= self.time_cubic.F_as_ratio(time / self.time_limit * 500)
            ratio *= self.debt_paying_speed

            # Calculate the delta
            dx, dy = ratio * self.debt[0], ratio * self.debt[1]

            return dx, dy

    # The delta is 'not' occured, so we change the force before the change occurs
    def update_as_delta(self, dx, dy):

        if self.target_position == None or (dx == 0 and dy == 0):
            return
        
        if self.slider_enabled:
            dx *= self.slider_k
            dy *= self.slider_k

        # TODO: add exception handling
        self.real_position[0] += dx
        self.real_position[1] += dy

        cx, cy, _, _ = gaussian_filter(self.real_position[0], self.real_position[1], self.target_position[0], self.target_position[1])

        self.last_position = cx, cy
        mdx, mdy = self.mitigate_error(dx, dy)
        self.last_position = cx + mdx, cy + mdy
        self.set_position(cx + mdx, cy + mdy)

    def update(self):
        
        if self.target_position == None or self.last_position == self.get_position():
            return
        
        dx, dy = self.get_position() - self.last_position

        self.update_as_delta(dx, dy)


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
            X_new[i,j], Y_new[i,j], _, _ = gaussian_filter(X[i,j], Y[i,j], 720, 500)

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