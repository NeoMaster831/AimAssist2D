# v2

import numpy as np

def potential_energy(x, y, target_pos, U0, sigma):
    # 잠재 에너지 함수 U(x, y)
    xt, yt = target_pos
    return U0 * np.exp(-((x - xt)**2 + (y - yt)**2) / (2 * sigma**2))

def force_field(x, y, target_pos, U0, sigma):
    # 힘 벡터 F(x, y) = ∇U(x, y)
    xt, yt = target_pos
    Fx = -((x - xt) / sigma**2) * U0 * np.exp(-((x - xt)**2 + (y - yt)**2) / (2 * sigma**2))
    Fy = -((y - yt) / sigma**2) * U0 * np.exp(-((x - xt)**2 + (y - yt)**2) / (2 * sigma**2))
    return Fx, Fy

def alpha_function(d, R, n):
    # 거리 기반 가중치 함수 α(d)
    alpha = np.where(d <= R, 1 - (d / R)**n, 0)
    return alpha

class AimAssist:
    def __init__(self, res_factor):
        self.active = True
        self.U0 = 1000.0 * res_factor
        self.sigma = 675.0 * res_factor
        self.strength = 5.0
        self.R = 150.0 * res_factor
        self.n = 1.125
        self.f_mitigation = 3.5

    def get_fx_fy(self, player_pos, target_pos):
        x_in, y_in = player_pos

        Fx, Fy = force_field(x_in, y_in, target_pos, self.U0, self.sigma)

        d = np.hypot(x_in - target_pos[0], y_in - target_pos[1])

        alpha = alpha_function(d, self.R, self.n)

        Fx *= alpha * self.strength
        Fy *= alpha * self.strength

        if abs(Fx) < 1:
            Fx *= self.f_mitigation
        if abs(Fy) < 1:
            Fy *= self.f_mitigation
        print(Fx, Fy)

        return Fx, Fy