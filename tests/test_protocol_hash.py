from systemictau_declare.protocol import Protocol, protocol_hash, _load_yaml, _protocol_yaml_path

# Payload SHA-256 of protocols/frozen_v1.yaml (canonical JSON, keys sorted).
# A change of any hashed field MUST update this pin and bump the protocol name.
PINNED_FROZEN_V1_HASH = (
    "f04909e497ae9fae7a006f6208286acb7bf5f04a1f1d85fd611b5dc8a97c06f6"
)


def test_frozen_v1_hash_stable_across_calls():
    a = Protocol.frozen_v1()
    b = Protocol.frozen_v1()
    assert a.yaml_hash == b.yaml_hash == PINNED_FROZEN_V1_HASH
    assert len(a.yaml_hash) == 64
    data = _load_yaml(_protocol_yaml_path("frozen_v1"))
    assert protocol_hash(data) == a.yaml_hash
    # second process-equivalent: hash(canonical json) does not depend on object identity
    assert protocol_hash(data) == protocol_hash(dict(data))


def test_hash_changes_if_window_changes():
    data = _load_yaml(_protocol_yaml_path("frozen_v1"))
    h0 = protocol_hash(data)
    data = dict(data)
    data["window"] = 21
    assert protocol_hash(data) != h0
