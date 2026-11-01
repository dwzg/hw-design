import pytest

from hwdesign.mcad.gasket import gasket_cord, gasket_tpu, lindley, shore_to_E


def test_shore_to_modulus_is_plausible_and_monotonic():
    # Gent's relation: about 3-4 MPa at 60 Shore A for silicone
    assert 2.5 < shore_to_E(60) < 5.0
    assert shore_to_E(50) < shore_to_E(60) < shore_to_E(70)


def test_lindley_grows_with_squeeze():
    assert lindley(0.0) == 0
    assert lindley(0.1) < lindley(0.2) < lindley(0.3)


@pytest.mark.parametrize("make", [lambda: gasket_cord(1.5, 55, 1.2), lambda: gasket_tpu(1.2, 1.5, 1.2)])
def test_force_drops_to_zero_when_the_gap_opens(make):
    f, s0 = make()
    assert s0 == pytest.approx(0.3)
    assert f(0.0)[0] > 0
    assert f(s0)[0] == 0 and f(s0 + 0.1)[0] == 0
    assert f(0.0)[0] > f(s0 / 2)[0]
