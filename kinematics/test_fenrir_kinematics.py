# =============================================================================
# PRODUCTION TEST SUITE — copied VERBATIM from the private FENRIR development
# repository (libs/fenrir_kinematics/test_fenrir_kinematics.py) on 2026-07-17.
# Runs publicly in CI on every push (see badge in the README).
# =============================================================================
"""Tests for fenrir_kinematics. Run: python3 test_fenrir_kinematics.py (or pytest)."""
import numpy as np

from fenrir_kinematics import (
    leg_fk,
    leg_ik,
    leg_ik_velocity,
    leg_jacobian,
    leg_statics,
)

L1, L2, L3 = 0.08, 0.20, 0.20
RNG = np.random.default_rng(42)


def random_joints(n: int) -> np.ndarray:
    """Random configurations within physical limits, knee strictly back."""
    return RNG.uniform(
        low=[-np.pi / 4, -np.pi / 4, -np.deg2rad(150)],
        high=[np.pi / 4, np.pi / 4, -np.deg2rad(30)],
        size=(n, 3),
    )


def test_roundtrip_position_and_branch(samples: int = 10_000) -> None:
    """FK(IK(FK(th))) == FK(th) AND IK returns the same solution branch."""
    max_pos_err = 0.0
    max_ang_err = 0.0
    n_branch_checked = 0
    for th in random_joints(samples):
        p = leg_fk(th, L1, L2, L3)
        th_solved = leg_ik(p, L1, L2, L3, knee_back=True)
        max_pos_err = max(
            max_pos_err, np.linalg.norm(leg_fk(th_solved, L1, L2, L3) - p)
        )
        # Branch check: IK's h = sqrt(...) convention assumes the foot sits
        # BELOW the abduction axis within the leg plane (h > 0) — true for
        # all gait poses. Extreme tuck (h < 0) has a second valid abduction
        # branch that reaches the same point with different angles, so exact
        # angle recovery is only guaranteed in the h > 0 regime.
        h = L2 * np.cos(th[1]) + L3 * np.cos(th[1] + th[2])
        if h > 0.01:
            n_branch_checked += 1
            max_ang_err = max(max_ang_err, np.max(np.abs(th_solved - th)))
    assert max_pos_err < 1e-9, f"position round-trip error {max_pos_err:.3e}"
    assert max_ang_err < 1e-9, f"joint round-trip error {max_ang_err:.3e}"
    assert n_branch_checked > samples * 0.8, "too few h>0 samples for branch check"
    print(
        f"roundtrip        OK  pos {max_pos_err:.3e} m, "
        f"ang {max_ang_err:.3e} rad ({n_branch_checked} branch-checked)"
    )


def test_jacobian_vs_finite_differences(samples: int = 2_000) -> None:
    """Analytic J must match central finite differences of FK."""
    eps = 1e-6
    worst = 0.0
    for th in random_joints(samples):
        J = leg_jacobian(th, L1, L2, L3)
        J_fd = np.zeros((3, 3))
        for j in range(3):
            d = np.zeros(3)
            d[j] = eps
            J_fd[:, j] = (
                leg_fk(th + d, L1, L2, L3) - leg_fk(th - d, L1, L2, L3)
            ) / (2 * eps)
        worst = max(worst, np.max(np.abs(J - J_fd)))
    assert worst < 1e-6, f"Jacobian mismatch {worst:.3e}"
    print(f"jacobian vs FD   OK  worst element error {worst:.3e}")


def test_determinant_closed_form(samples: int = 2_000) -> None:
    """det J == -L2*L3*h*sin(th3) everywhere."""
    worst = 0.0
    for th in random_joints(samples):
        h = L2 * np.cos(th[1]) + L3 * np.cos(th[1] + th[2])
        det_closed = -L2 * L3 * h * np.sin(th[2])
        det_num = np.linalg.det(leg_jacobian(th, L1, L2, L3))
        worst = max(worst, abs(det_num - det_closed))
    assert worst < 1e-12, f"determinant mismatch {worst:.3e}"
    print(f"det closed form  OK  worst error {worst:.3e}")


def test_statics_standing_pose() -> None:
    """Foot under hip: zero hip-pitch torque; knee and abduction match hand calc."""
    p_stand = np.array([0.0, L1, -0.30])
    th = leg_ik(p_stand, L1, L2, L3)
    tau = leg_statics(th, np.array([0.0, 0.0, 22.0]), L1, L2, L3)
    assert abs(tau[1]) < 1e-9, "hip pitch torque must vanish with foot under hip"
    assert abs(tau[0] - 22.0 * L1) < 1e-9, "abduction torque must equal F*L1"
    # Exact: beta = arccos(r/(2*L2)) = 41.40962 deg, tau3 = 22*L3*sin(-beta)
    assert abs(tau[2] - (-2.91033)) < 1e-4, "knee torque should be -2.9103 N*m"
    print(f"statics standing OK  tau = {np.round(tau, 4)} N*m")


def test_velocity_dls_tracks_and_stays_bounded() -> None:
    """DLS inverse tracks well away from singularity, stays finite near it."""
    th = leg_ik(np.array([0.0, L1, -0.30]), L1, L2, L3)
    v_des = np.array([0.1, 0.0, 0.05])
    th_dot = leg_ik_velocity(th, v_des, L1, L2, L3)
    v_actual = leg_jacobian(th, L1, L2, L3) @ th_dot
    assert np.linalg.norm(v_actual - v_des) < 1e-3, "DLS tracking error too large"
    # Nearly straight knee (1 deg from singular): rates must remain finite/sane.
    th_sing = np.array([0.0, 0.1, -np.deg2rad(1.0)])
    th_dot_sing = leg_ik_velocity(th_sing, v_des, L1, L2, L3)
    assert np.all(np.isfinite(th_dot_sing))
    assert np.linalg.norm(th_dot_sing) < 1e3, "DLS failed to bound joint rates"
    print("velocity DLS     OK  tracks off-singularity, bounded near it")


if __name__ == "__main__":
    test_roundtrip_position_and_branch()
    test_jacobian_vs_finite_differences()
    test_determinant_closed_form()
    test_statics_standing_pose()
    test_velocity_dls_tracks_and_stays_bounded()
    print("\nall tests passed")
