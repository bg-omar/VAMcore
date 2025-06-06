import pytest

vambindings = pytest.importorskip("vambindings")


def test_compute_helicity_simple():
    velocity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    vorticity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    H = vambindings.compute_helicity(velocity, vorticity)
    assert H == pytest.approx(1.0)


def test_compute_kinetic_energy():
    velocity = [[1.0, 2.0, 2.0], [0.0, 0.0, 0.0]]
    rho_ae = 2.0
    E = vambindings.compute_kinetic_energy(velocity, rho_ae)
    assert E == pytest.approx(9.0)


def test_biot_savart_symmetry_zero():
    r = [0.0, 0.0, 0.0]
    X = [[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]
    T = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    v = vambindings.biot_savart_velocity(r, X, T)
    assert v[0] == pytest.approx(0.0, abs=1e-7)
    assert v[1] == pytest.approx(0.0, abs=1e-7)
    assert v[2] == pytest.approx(0.0, abs=1e-7)


def test_time_dilation_map():
    tangents = [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    factors = vambindings.compute_time_dilation_map(tangents, 2.0)
    assert factors[0] == pytest.approx((1.0 - 1.0/4)**0.5)
    assert factors[1] == pytest.approx(1.0)
