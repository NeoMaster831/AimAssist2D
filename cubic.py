import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

class MonotoneCubic:
    def __init__(self, a, b, k1, k2, k3, s, reversed=False):
        self.a = a
        self.b = b
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.s = s
        self.reversed = reversed
        
    def F(self, x):
        points_x = [0, self.a, self.b, self.s]
        y0 = 0
        y1 = y0 + self.k1 * self.a
        y2 = y1 + self.k2 * (self.b - self.a)
        y3 = y2 + self.k3 * (self.s - self.b)
        points_y = [y0, y1, y2, y3]
        interpolator = PchipInterpolator(points_x, points_y)
        
        if self.reversed:
            return interpolator(self.s - x)
        return interpolator(x)

    def F_as_ratio(self, x):
        return self.F(x) / self.F(self.s)

if __name__ == "__main__":
    # 파라미터 설정
    a = 150      # 첫 번째 전환점
    b = 350      # 두 번째 전환점
    k1 = 1      # 첫 번째 구간 기울기
    k2 = 3      # 두 번째 구간 기울기
    k3 = 1      # 세 번째 구간 기울기
    s = 500

    # 인터폴레이터 생성
    cubic = MonotoneCubic(a, b, k1, k2, k3, s, reversed=True)

    # x 값 생성
    x = np.linspace(0, s, s)
    y = cubic.F(x)

    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Monotonic Cubic Function (PCHIP)', color='blue')
    plt.axvline(x=a, color='red', linestyle='--', label='a (전환점)')
    plt.axvline(x=b, color='green', linestyle='--', label='b (전환점)')
    plt.scatter([0, a, b, s], [cubic.F(0), cubic.F(a), cubic.F(b), cubic.F(s)], color='black')  # 키 포인트 표시
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Monotonic Cubic S-Shaped Function using PCHIP')
    plt.legend()
    plt.grid(True)
    plt.show()
