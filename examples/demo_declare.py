"""Demo: declare the generator on G0 (should not claim an event)."""

from pathlib import Path

from systemictau_declare import (
    Protocol,
    coupled_logistic,
    declare,
    g0_independent_ar,
    write_report,
)

HERE = Path(__file__).resolve().parent


def main() -> None:
    # Fast exploratory B so the demo finishes on a laptop.
    # A citable run uses Protocol.frozen_v1() with B=99.
    P = Protocol.exploratory(B=9, surrogate="permute")

    X0 = g0_independent_ar(T=240, N=4, seed=0)
    r0 = declare(X0, protocol=P)
    p0 = HERE / "demo_g0_report.html"
    write_report(r0, p0)
    print("G0 FAR:", r0.seal.far, "claimed:", r0.seal.event_claimed, "->", p0)

    X1 = coupled_logistic(T=400, N=4, r=3.7, seed=1)
    r1 = declare(X1, protocol=P)
    p1 = HERE / "demo_logistic_report.html"
    write_report(r1, p1)
    print("logistic FAR:", r1.seal.far, "claimed:", r1.seal.event_claimed, "->", p1)
    print(r1.summary())


if __name__ == "__main__":
    main()
