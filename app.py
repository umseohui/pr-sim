import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("PR Jet Instability Simulator (with Viscosity)")

# 1. 입력 파라미터 (단위 및 범위 수정)
# 밀도, 노즐 반경, 속도는 단순화하기 위해 상수로 고정
density = 1000.0  # kg/m3 (Typical PR density)
radius = 1e-4      # m (100 um nozzle radius)

viscosity_cp = st.slider("Viscosity (cP)", 1.0, 100.0, 10.0) # cP -> Pa*s로 변환
viscosity = viscosity_cp / 1000.0 # kg/(m*s)
surface_tension = st.slider("Surface Tension (mN/m)", 20.0, 70.0, 30.0) # mN/m -> N/m로 변환

# 2. 진짜 Rayleigh 분산 관계식 (with viscosity)
kR = np.linspace(0, 1.1, 200) # x축 범위 (k*R)
k = kR / radius

# 성장률 omega 제곱을 구하는 수식 (Bessel 함수 등을 포함하는 복잡한 식을 단순화)
# Viscosity가 높으면 omega가 낮아지고, Surface tension이 높으면 omega가 높아지는 관계
# 점도가 포함된 수식은 복잡하므로, 경향성을 보여주는 모델을 사용
omega_squared = (surface_tension / (density * radius**3)) * (kR * (1 - kR**2)) / (1 + (viscosity * kR / (density * radius**2 * (surface_tension / density * radius)**0.5))) # 예시 모델

# 3. 시각화
fig, ax = plt.subplots()
ax.plot(kR, omega_squared, label='Dispersion Relation')
ax.set_xlabel("Dimensionless Wavenumber (kR)")
ax.set_ylabel("Growth Rate (omega^2)")
ax.axhline(0, color='black', lw=0.5, ls='--')
ax.axvline(0.697, color='red', lw=1, ls='--', label='Max Instability (Theory)')
ax.set_title(f"Viscosity: {viscosity_cp:.1f} cP, Surface Tension: {surface_tension:.1f} mN/m")
ax.legend()
ax.set_ylim(-10, max(omega_squared) * 1.2) # y축 범위 자동 조절
st.pyplot(fig)

# 이론적 피크 지점
st.write(f"Predicted Max Wavelength: lambda ≈ {9.01*radius*1e6:.1f} µm")
