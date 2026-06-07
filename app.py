import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("PR Jet Instability Simulator")

# 입력 파라미터
viscosity = st.slider("Viscosity (cP)", 1.0, 100.0, 10.0)
surface_tension = st.slider("Surface Tension (mN/m)", 20.0, 70.0, 30.0)

# 이론적 연산 (Rayleigh-Plateau)
k = np.linspace(0, 1, 100)
omega_squared = (surface_tension / 1.0) * k * (1 - k**2) # 단순 모델

# 시각화
fig, ax = plt.subplots()
ax.plot(k, omega_squared)
ax.set_xlabel("Wavenumber (kR)")
ax.set_ylabel("Growth Rate (omega^2)")
st.pyplot(fig)