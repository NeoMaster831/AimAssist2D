import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from ipywidgets import interact, FloatSlider
import warnings

warnings.filterwarnings('ignore')  # 경고 메시지 무시

def potential_energy(x, y, target_pos, U0, sigma):
    # 잠재 에너지 함수 U(x, y)
    xt, yt = target_pos
    return U0 * np.exp(-((x - xt)**2 + (y - yt)**2) / (2 * sigma**2))

def force_field(x, y, target_pos, U0, sigma):
    # 힘 벡터 F(x, y) = ∇U(x, y)
    xt, yt = target_pos
    Fx = ((x - xt) / sigma**2) * U0 * np.exp(-((x - xt)**2 + (y - yt)**2) / (2 * sigma**2))
    Fy = ((y - yt) / sigma**2) * U0 * np.exp(-((x - xt)**2 + (y - yt)**2) / (2 * sigma**2))
    return Fx, Fy

def alpha_function(d, R, n):
    # 거리 기반 가중치 함수 α(d)
    alpha = np.where(d <= R, 1 - (d / R)**n, 0)
    return alpha

def aim_assist(input_vector, player_pos, target_pos, U0, sigma, R, n, strength):
    x_in, y_in = player_pos
    vx_in, vy_in = input_vector

    # 플레이어 위치에서 힘 계산
    Fx, Fy = force_field(x_in, y_in, target_pos, U0, sigma)

    # 타겟과의 거리 계산
    d = np.hypot(x_in - target_pos[0], y_in - target_pos[1])

    # 가중치 함수 계산
    alpha = alpha_function(d, R, n)

    # 에임 어시스트 강도 적용
    Fx *= alpha * strength
    Fy *= alpha * strength

    # 출력 벡터 계산
    vx_out = vx_in + Fx
    vy_out = vy_in + Fy

    return np.array([vx_out, vy_out])

def plot_aim_assist(U0, sigma, strength, R):
    # 설정
    player_pos = np.array([200, 150])    # 플레이어 위치
    target_pos = np.array([300, 200])    # 타겟 위치

    n = 1.5                            # α(d) 함수의 지수 (감쇠 정도 조절)

    # 3D 그래프를 위한 그리드 생성
    x = np.linspace(0, 400, 100)
    y = np.linspace(0, 300, 100)
    X, Y = np.meshgrid(x, y)

    # 잠재 에너지 함수 계산
    Z = potential_energy(X, Y, target_pos, U0, sigma)

    # 시각화
    fig = plt.figure(figsize=(12, 6))

    # 3D 잠재 에너지 함수 그래프
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot_surface(X, Y, Z, cmap=cm.viridis, edgecolor='none', alpha=0.8)
    ax1.set_title('Potential Energy Function U(x, y)')
    ax1.set_xlabel('X coords')
    ax1.set_ylabel('Y coords')
    ax1.set_zlabel('U(x, y)')

    # 플레이어와 타겟 위치 표시
    ax1.scatter(player_pos[0], player_pos[1], potential_energy(player_pos[0], player_pos[1], target_pos, U0, sigma), color='blue', label='Cursor Location')
    ax1.scatter(target_pos[0], target_pos[1], potential_energy(target_pos[0], target_pos[1], target_pos, U0, sigma), color='red', label='Target Location')
    ax1.legend()

    # 2D 힘 벡터 필드 및 에임 어시스트 적용 전후 비교
    ax2 = fig.add_subplot(122)
    ax2.contourf(X, Y, Z, levels=50, cmap=cm.viridis, alpha=0.5)
    ax2.set_title('Aim Assist Vector Field')
    ax2.set_xlabel('X coords')
    ax2.set_ylabel('Y coords')

    # 입력 벡터와 출력 벡터 계산 및 시각화
    angles = np.linspace(0, 2 * np.pi, 36)
    input_vectors = np.array([np.array([np.cos(angle), np.sin(angle)]) for angle in angles])

    # 입력 벡터를 파란색 화살표로 표시
    for v_in in input_vectors:
        ax2.quiver(player_pos[0], player_pos[1], v_in[0], v_in[1], color='blue', angles='xy', scale_units='xy', scale=5)

    # 출력 벡터를 빨간색 화살표로 표시
    for v_in in input_vectors:
        v_out = aim_assist(v_in, player_pos, target_pos, U0, sigma, R, n, strength)
        ax2.quiver(player_pos[0], player_pos[1], v_out[0], v_out[1], color='red', angles='xy', scale_units='xy', scale=5)

    # 타겟 위치 표시
    ax2.plot(target_pos[0], target_pos[1], 'ro', label='Target Location')

    # 에임 어시스트 범위 표시
    circle = plt.Circle((player_pos[0], player_pos[1]), R, color='green', fill=False, linestyle='--', alpha=0.5, label='Aim Assist Range')
    ax2.add_artist(circle)

    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()
    plt.show()

# 인터랙티브 위젯 생성

interact(plot_aim_assist,
         U0=FloatSlider(min=0.1, max=20.0, step=0.1, value=10000.0, description='U0'),
         sigma=FloatSlider(min=0.1, max=5.0, step=0.1, value=50.0, description='Sigma'),
         strength=FloatSlider(min=0.1, max=1.0, step=0.01, value=0.5, description='Strength'),
         R=FloatSlider(min=1.0, max=20.0, step=0.1, value=100.0, description="R")); 
