import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.special import iv

# =========================================================
# Page setup
# =========================================================
st.set_page_config(
    page_title="Photoresist Dispensing Jet Simulator",
    layout="wide"
)

st.title("Photoresist Dispensing Jet Simulator")
st.subheader("Rayleigh-Plateau Instability and Substrate Impact")

st.write(
    """
    This simulator predicts the stability of a photoresist dispensing jet using
    Rayleigh-Plateau instability theory. The model estimates the growth-rate
    spectrum, most unstable wavelength, breakup time, and breakup distance.
    """
)

# =========================================================
# Sidebar inputs
# =========================================================
st.sidebar.header("Input Parameters")

r0_um = st.sidebar.slider(
    "Nozzle radius r₀ (μm)",
    min_value=5.0,
    max_value=200.0,
    value=50.0,
    step=5.0
)

U = st.sidebar.slider(
    "Ejection velocity U (m/s)",
    min_value=0.01,
    max_value=5.0,
    value=0.50,
    step=0.01
)

eta_cP = st.sidebar.slider(
    "Viscosity η (cP)",
    min_value=0.5,
    max_value=100.0,
    value=10.0,
    step=0.5
)

gamma_mNm = st.sidebar.slider(
    "Surface tension γ (mN/m)",
    min_value=10.0,
    max_value=80.0,
    value=30.0,
    step=1.0
)

rho = st.sidebar.slider(
    "Density ρ (kg/m³)",
    min_value=700.0,
    max_value=1500.0,
    value=1000.0,
    step=10.0
)

L_um = st.sidebar.slider(
    "Distance to substrate L (μm)",
    min_value=50.0,
    max_value=2000.0,
    value=200.0,
    step=50.0
)

epsilon0_ratio = st.sidebar.slider(
    "Initial perturbation ε₀ / r₀",
    min_value=0.001,
    max_value=0.100,
    value=0.010,
    step=0.001
)

breakup_ratio = st.sidebar.slider(
    "Breakup criterion r_min / r₀",
    min_value=0.01,
    max_value=0.50,
    value=0.10,
    step=0.01
)

# =========================================================
# Unit conversion
# =========================================================
r0 = r0_um * 1e-6          # μm → m
eta = eta_cP * 1e-3       # cP → Pa·s
gamma = gamma_mNm * 1e-3  # mN/m → N/m
L = L_um * 1e-6           # μm → m
epsilon0 = epsilon0_ratio * r0

# =========================================================
# Dimensionless wavenumber range
# kR < 1 is unstable for Rayleigh-Plateau instability
# =========================================================
x = np.linspace(0.01, 1.20, 800)  # x = k*r0
k = x / r0

# =========================================================
# Inviscid Rayleigh-Plateau growth rate
# omega^2 = gamma/(rho*R^3) * I1(kR)/I0(kR) * (kR)(1-k^2R^2)
# =========================================================
I0 = iv(0, x)
I1 = iv(1, x)

omega2_inviscid = (gamma / (rho * r0**3)) * (I1 / I0) * x * (1 - x**2)

# Negative values are stable, so growth rate is set to 0 for prediction
omega_inviscid = np.sqrt(np.maximum(omega2_inviscid, 0))

# =========================================================
# Simple viscosity damping correction
# This is an engineering approximation, not the full viscous dispersion relation.
# Higher viscosity suppresses instability growth.
# =========================================================
Ca = eta * U / gamma

damping_factor = 1 / (1 + 3 * Ca)
omega_effective = omega_inviscid * damping_factor

# =========================================================
# Most unstable mode
# =========================================================
idx_max = np.argmax(omega_effective)
omega_max = omega_effective[idx_max]
k_max = k[idx_max]
x_max = x[idx_max]

lambda_max = 2 * np.pi / k_max

# =========================================================
# Breakup time and breakup distance
# Perturbation growth: epsilon(t) = epsilon0 exp(omega t)
# Breakup assumed when epsilon reaches (1 - breakup_ratio)*r0
# =========================================================
epsilon_break = (1 - breakup_ratio) * r0

if omega_max > 0 and epsilon_break > epsilon0:
    t_break = np.log(epsilon_break / epsilon0) / omega_max
    L_break = U * t_break
else:
    t_break = np.inf
    L_break = np.inf

t_impact = L / U

breaks_before_wafer = L_break < L

# =========================================================
# Summary metrics
# =========================================================
st.header("Simulation Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Maximum growth rate ωmax", f"{omega_max:.2e} 1/s")
    st.metric("Most unstable kR", f"{x_max:.3f}")

with col2:
    st.metric("Most unstable wavelength λmax", f"{lambda_max * 1e6:.2f} μm")
    st.metric("Breakup time", f"{t_break * 1e3:.3f} ms" if np.isfinite(t_break) else "No breakup")

with col3:
    st.metric("Breakup distance", f"{L_break * 1e6:.2f} μm" if np.isfinite(L_break) else "No breakup")
    st.metric("Time to substrate", f"{t_impact * 1e3:.3f} ms")

# =========================================================
# Stability judgment
# =========================================================
st.header("Stability Judgment")

if breaks_before_wafer:
    st.error(
        "The jet is predicted to break before reaching the wafer. "
        "This condition may produce satellite droplets and coating non-uniformity."
    )
else:
    st.success(
        "The jet is predicted to reach the wafer before breakup. "
        "This condition is more favorable for stable photoresist coating."
    )

# =========================================================
# Plot 1: Growth-rate spectrum
# =========================================================
st.header("Growth-Rate Spectrum")

fig1, ax1 = plt.subplots(figsize=(8, 5))

ax1.plot(x, omega_effective, label="Effective growth rate")
ax1.plot(x, omega_inviscid, linestyle="--", label="Inviscid growth rate")
ax1.axvline(x_max, linestyle=":", label="Most unstable mode")
ax1.axvline(1.0, linestyle="-.", label="Stability boundary kR = 1")

ax1.set_xlabel("Dimensionless wavenumber kR")
ax1.set_ylabel("Growth rate ω(k) [1/s]")
ax1.set_title("Rayleigh-Plateau Growth-Rate Spectrum")
ax1.legend()
ax1.grid(True)

st.pyplot(fig1)

st.write(
    """
    The region where **kR < 1** corresponds to unstable long-wavelength disturbances.
    In wavelength form, this condition is equivalent to **λ > 2πr₀**.
    """
)

# =========================================================
# Plot 2: Breakup distance compared with substrate distance
# =========================================================
st.header("Breakup Distance vs. Substrate Distance")

fig2, ax2 = plt.subplots(figsize=(8, 3))

ax2.axvline(L * 1e6, label="Substrate position L")
if np.isfinite(L_break):
    ax2.axvline(L_break * 1e6, linestyle="--", label="Predicted breakup distance")

ax2.set_xlim(0, max(L * 1e6 * 1.3, min(L_break * 1e6 * 1.3, 5000) if np.isfinite(L_break) else L * 1e6 * 1.3))
ax2.set_ylim(0, 1)
ax2.set_yticks([])
ax2.set_xlabel("Distance from nozzle (μm)")
ax2.set_title("Breakup Distance Compared with Substrate Location")
ax2.legend()
ax2.grid(True)

st.pyplot(fig2)

# =========================================================
# Animation-like visualization using time slider
# =========================================================
st.header("Liquid Column Deformation Visualization")

st.write(
    """
    The jet radius is visualized using:

    r(z,t) = r₀ + ε₀ exp(ωmax t) cos(kmax z)

    As time increases, the surface disturbance grows and the liquid column becomes more wavy.
    """
)

if np.isfinite(t_break):
    t_anim = st.slider(
        "Animation time t (ms)",
        min_value=0.0,
        max_value=float(t_break * 1e3),
        value=0.0,
        step=max(float(t_break * 1e3) / 100, 0.001)
    )
    t_current = t_anim * 1e-3
else:
    t_current = 0.0

z = np.linspace(0, max(lambda_max * 2, L), 600)
epsilon_t = epsilon0 * np.exp(omega_max * t_current)

r_profile = r0 + epsilon_t * np.cos(k_max * z)

# Avoid negative radius in visualization
r_profile = np.maximum(r_profile, 0)

fig3, ax3 = plt.subplots(figsize=(10, 4))

ax3.plot(z * 1e6, r_profile * 1e6, label="Upper surface")
ax3.plot(z * 1e6, -r_profile * 1e6, label="Lower surface")

ax3.axvline(L * 1e6, linestyle="--", label="Substrate")
ax3.set_xlabel("Axial position z (μm)")
ax3.set_ylabel("Jet radius r (μm)")
ax3.set_title("PR Jet Surface Deformation")
ax3.legend()
ax3.grid(True)

st.pyplot(fig3)

# =========================================================
# Explanation section
# =========================================================
st.header("Physical Interpretation")

st.write(
    f"""
    **Input summary**

    - Nozzle radius: {r0_um:.1f} μm  
    - Ejection velocity: {U:.2f} m/s  
    - Viscosity: {eta_cP:.1f} cP  
    - Surface tension: {gamma_mNm:.1f} mN/m  
    - Distance to substrate: {L_um:.1f} μm  

    **Interpretation**

    Surface tension drives the Rayleigh-Plateau instability by reducing the surface area
    of the liquid column. Viscosity resists this deformation and reduces the growth rate.
    The ejection velocity controls the flight time between the nozzle and the wafer.
    A stable process requires the jet to reach the wafer before the instability grows
    enough to cause breakup.
    """
)

st.info(
    """
    Note: This simulator uses a simplified viscous damping correction.
    It is intended for educational and engineering interpretation, not as a replacement
    for full CFD or industrial lithography track simulation.
    """
)
