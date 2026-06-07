import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("PR Jet Instability Simulator")

# 파라미터 입력
viscosity_cp = st.slider("Viscosity (cP)", 1.0, 100.0, 10.0)
surface_tension = st.slider("Surface Tension (mN/m)", 20.0, 70.0, 30.0)

# kR 범위 설정
kR = np.linspace(0.01, 1.1, 100)

# Rayleigh-Plateau 분산 관계식 (점도 감쇠항이 강력하게 적용된 모델)
# Viscosity가 분모에 들어가서 증가할수록 성장률(omega)을 강하게 억제하도록 설정
omega_squared = (surface_tension / 20.0) * (kR * (1 - kR**2)) / (1 + (viscosity_cp / 5.0) * kR)

# 시각화
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(kR, omega_squared, lw=3, color='#1f77b4')
ax.set_xlabel("Dimensionless Wavenumber (kR)", fontsize=12)
ax.set_ylabel("Growth Rate (omega^2)", fontsize=12)
ax.set_title("Dispersion Relation Curve", fontsize=14)
ax.grid(True, linestyle='--', alpha=0.6)

# y축 범위 고정 (그래프 변동을 시각적으로 크게 보기 위함)
ax.set_ylim(0, 5) 

st.pyplot(fig)
