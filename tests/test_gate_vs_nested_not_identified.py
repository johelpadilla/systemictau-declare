from systemictau_declare.schema import DeclarationReport, GateGenerator, NestedDepth, AmplitudeContrast, Seal
from systemictau_declare import Protocol
import numpy as np
import inspect


def test_schema_keeps_two_clocks_and_two_level3_fields():
    gate_doc = GateGenerator.__doc__ or ""
    nested_doc = NestedDepth.__doc__ or ""
    assert "not nested" in gate_doc.lower() or "not laboratory" in gate_doc.lower()
    assert "primary" in nested_doc.lower()
    # fields remain distinct on the dataclass
    assert "dT" in GateGenerator.__dataclass_fields__
    assert "T_n" in GateGenerator.__dataclass_fields__
    assert "excess3" in NestedDepth.__dataclass_fields__
    assert "dT" not in NestedDepth.__dataclass_fields__
    assert "excess3" not in GateGenerator.__dataclass_fields__


def test_as_dict_does_not_alias_dt_and_excess3():
    T = 5
    nan = np.full(T, np.nan)
    from systemictau_declare.schema import DeclarationReport

    dummy = DeclarationReport(
        t=np.arange(T),
        X_shape=(T, 2),
        protocol_name="frozen_v1",
        protocol_hash="abc",
        exploratory=False,
        tau_s=nan,
        gate=GateGenerator(T_n=np.ones(T), dT=np.full(T, 0.2), g=np.ones(T), depth=np.zeros(T), delta_T=1.0),
        nested=NestedDepth(phi1=nan, phi2=nan, phi3=nan, excess3=np.full(T, 0.9), delta_excess3=0.3, z_excess3=1.0),
        regime=np.array(["stable"] * T, dtype=object),
        lam_core=nan,
        tt_core=nan,
        core_hyper=np.zeros(T, dtype=bool),
        amp=AmplitudeContrast(nan, nan, 0.0, 0.0, 0.0, 0.0, 0, 0),
        delta_tau_s=0.0,
        z_tau_s=0.0,
        p_surrogate=1.0,
        n_surrogates=0,
        surrogate_method="phase_shuffle",
        sign_tau_excess3=0,
        sign_tau_variance=0,
        seal=Seal(far="undefined"),
        non_identification=Protocol.frozen_v1().non_identification,
    )
    d = dummy.as_dict()
    assert "dT" in d and "excess3" in d
    assert d["dT"] != d["excess3"]
    assert d["delta_T_n"] != d["delta_excess3"]
    assert any("not" in line.lower() and "excess" in line.lower() for line in d["non_identification"])


def test_declare_docstring_refuses_predict():
    from systemictau_declare import declare

    doc = inspect.getdoc(declare) or ""
    assert "declare" in doc.lower()
    assert "predict_outbreak" in doc
