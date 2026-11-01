"""Gasket estimates: Shore A to modulus (Gent), Lindley's O-ring/cord force law, and
force-deflection functions for a round cord and a flat TPU bead. Estimates, not measurements:
use them to size squeeze and screw spacing, then check on the printed part."""


def shore_to_E(sh):
    """Gent's relation, Shore A -> Young's modulus (MPa)."""
    return 0.0981 * (56 + 7.62336 * sh) / (0.137505 * (254 - 2.54 * sh))


def lindley(eps):
    """O-ring/cord line force per (E * d), Lindley 1967."""
    return 1.25 * eps ** 1.5 + 50 * eps ** 6


def lindley_d(eps):
    return 1.875 * eps ** 0.5 + 300 * eps ** 5


def gasket_cord(d, shore, D):
    E = shore_to_E(shore)
    s0 = d - D

    def f(w):
        dl = s0 - w
        if dl <= 0:
            return 0.0, 0.0
        e = dl / d
        return E * d * lindley(e), E * lindley_d(e)
    return f, s0


def gasket_tpu(b, h0, D, E=26.0, nu=0.48):
    Ep = E / (1 - nu * nu)
    s0 = h0 - D

    def f(w):
        dl = s0 - w
        if dl <= 0:
            return 0.0, 0.0
        return b * Ep * dl / h0, b * Ep / h0
    return f, s0
