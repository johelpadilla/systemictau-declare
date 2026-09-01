from systemictau_declare.seals import make_seal


def test_no_controls_far_undefined():
    s = make_seal(
        controls=None,
        event_only=False,
        event_candidate=True,
        p_surrogate=0.001,
        p_threshold=0.05,
    )
    assert s.far == "undefined"
    assert s.event_claimed is False
    assert s.event_candidate is True


def test_event_only_seal():
    s = make_seal(
        controls=None,
        event_only=True,
        event_candidate=True,
        p_surrogate=0.0,
        p_threshold=0.05,
    )
    assert s.far == "event-only"
    assert s.event_claimed is False


def test_controls_estimated_far():
    s = make_seal(
        controls=[object()],
        event_only=False,
        event_candidate=True,
        p_surrogate=0.01,
        p_threshold=0.05,
        n_control_alarms=1,
        n_controls=10,
    )
    assert s.far == "estimated"
    assert s.far_value == 0.1
    assert s.event_claimed is True
