# =============================================================================
# PRODUCTION MODULE — copied VERBATIM from the private FENRIR development
# repository (libs/fenrir_kinematics/fenrir_kinematics.py) on 2026-07-17.
# This is the exact code the robot runs, together with its full test suite.
# =============================================================================
"""fenrir_kinematics — closed-form kinematics for the FENRIR 3-DOF leg.

Frame convention (per CLAUDE.md / REP-105): hip frame at the abduction axis,
x forward, y outward from body side, z up. Foot targets have z < 0.

Joint convention:
    th1 — hip abduction (roll about x), 0 = leg plane vertical
    th2 — hip pitch, 0 = thigh straight down, positive = forward
    th3 — knee, 0 = straight leg, negative = knee-backward flexion

Link parameters (config-driven per Rule 2 — never hardcode):
    L1 — lateral hip offset, L2 — thigh length, L3 — shank length.
    Right-side legs mirror by passing negative L1.

Convention boundary: leg_ik assumes the foot sits below the abduction axis
within the leg plane (in-plane reach h >= 0) — true for all stance/gait poses.
Extreme tucked configurations with h < 0 have a second valid abduction branch
that leg_ik will not return; a retargeted skill needing that regime requires
extending the solver (tracked as a known limitation, not a bug).

Workspace margin: the planning bound r <= margin*(L2+L3) is owned by
config/robot.yaml (workspace.extension_margin) — planners pass it explicitly.
This module only enforces the exact reach limits (see leg_ik guards).

Derivations: docs/decisions/2026-07-12-leg-ik-jacobian.md
"""
from __future__ import annotations

import numpy as np


class UnreachableTarget(ValueError):
    """Foot target lies outside the leg's reachable workspace."""


def leg_ik(
    p: np.ndarray, L1: float, L2: float, L3: float, knee_back: bool = True
) -> np.ndarray:
    """Solve joint angles (th1, th2, th3) for foot position p = (x, y, z).

    Raises UnreachableTarget if the target is outside the workspace.
    """
    x, y, z = p
    rho2 = y * y + z * z
    if rho2 < L1 * L1:
        raise UnreachableTarget("target inside hip offset radius")
    h = np.sqrt(rho2 - L1 * L1)
    th1 = np.arctan2(y, -z) - np.arctan2(L1, h)

    r2 = x * x + h * h
    r = np.sqrt(r2)
    if not (abs(L2 - L3) <= r <= (L2 + L3)):
        raise UnreachableTarget("target outside leg reach")

    phi = np.arccos(np.clip((L2 * L2 + L3 * L3 - r2) / (2 * L2 * L3), -1.0, 1.0))
    beta = np.arccos(np.clip((L2 * L2 + r2 - L3 * L3) / (2 * L2 * r), -1.0, 1.0))
    alpha = np.arctan2(x, h)

    s = 1.0 if knee_back else -1.0
    return np.array([th1, alpha + s * beta, -s * (np.pi - phi)])


def leg_fk(th: np.ndarray, L1: float, L2: float, L3: float) -> np.ndarray:
    """Foot position (x, y, z) in the hip frame from joint angles."""
    th1, th2, th3 = th
    x = L2 * np.sin(th2) + L3 * np.sin(th2 + th3)
    h = L2 * np.cos(th2) + L3 * np.cos(th2 + th3)
    y = h * np.sin(th1) + L1 * np.cos(th1)
    z = L1 * np.sin(th1) - h * np.cos(th1)
    return np.array([x, y, z])


def leg_jacobian(th: np.ndarray, L1: float, L2: float, L3: float) -> np.ndarray:
    """3x3 Jacobian J = d(x,y,z)/d(th1,th2,th3) of leg_fk at th.

    Closed form (see derivation doc):
        J = [[ 0,   h,       L3*c23      ],
             [-z,  -x*s1,   -L3*s23*s1   ],
             [ y,   x*c1,    L3*s23*c1   ]]
    with det J = -L2 * L3 * h * sin(th3). Singular at straight knee
    (sin th3 = 0) and at h = 0.
    """
    th1, th2, th3 = th
    s1, c1 = np.sin(th1), np.cos(th1)
    s23, c23 = np.sin(th2 + th3), np.cos(th2 + th3)
    x = L2 * np.sin(th2) + L3 * s23
    h = L2 * np.cos(th2) + L3 * c23
    y = h * s1 + L1 * c1
    z = L1 * s1 - h * c1
    return np.array(
        [
            [0.0, h, L3 * c23],
            [-z, -x * s1, -L3 * s23 * s1],
            [y, x * c1, L3 * s23 * c1],
        ]
    )


def leg_ik_velocity(
    th: np.ndarray,
    foot_vel: np.ndarray,
    L1: float,
    L2: float,
    L3: float,
    damping: float = 1e-3,
) -> np.ndarray:
    """Joint velocities for a desired foot velocity, damped least squares.

    th_dot = J^T (J J^T + damping^2 I)^-1 * foot_vel

    Well-behaved near singularities (bounded joint rates at the cost of a
    small tracking error). Control loops use THIS, never a raw inverse.
    """
    J = leg_jacobian(th, L1, L2, L3)
    JJt = J @ J.T + (damping * damping) * np.eye(3)
    return J.T @ np.linalg.solve(JJt, foot_vel)


def leg_statics(
    th: np.ndarray, foot_force: np.ndarray, L1: float, L2: float, L3: float
) -> np.ndarray:
    """Joint torques holding an external force applied at the foot: tau = J^T F."""
    return leg_jacobian(th, L1, L2, L3).T @ foot_force
