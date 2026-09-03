import uuid
from datetime import datetime, timezone
from app.services.audit.hash_chain import compute_event_hash, AuditHashChain


class MockAuditEvent:
    def __init__(self, prev, curr, payload, etype, t):
        self.id = str(uuid.uuid4())
        self.previous_hash = prev
        self.current_hash = curr
        self.event_payload_json = payload
        self.event_type = etype
        self.timestamp = t


def test_hash_chain_verification_clean():
    t1 = datetime(2026, 5, 21, 9, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 5, 21, 9, 1, 0, tzinfo=timezone.utc)

    p1 = '{"action":"init"}'
    h1 = compute_event_hash(None, {"action": "init"}, t1)
    e1 = MockAuditEvent(None, h1, p1, "INIT", t1)

    p2 = '{"action":"screen"}'
    h2 = compute_event_hash(h1, {"action": "screen"}, t2)
    e2 = MockAuditEvent(h1, h2, p2, "SCREEN", t2)

    res = AuditHashChain.verify_chain([e1, e2])
    assert res["status"] == "VERIFIED"
    assert res["chain_valid"] is True
    assert res["total_events"] == 2


def test_hash_chain_detects_tamper():
    t1 = datetime(2026, 5, 21, 9, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 5, 21, 9, 1, 0, tzinfo=timezone.utc)

    p1 = '{"action":"init"}'
    h1 = compute_event_hash(None, {"action": "init"}, t1)
    e1 = MockAuditEvent(None, h1, p1, "INIT", t1)

    p2 = '{"action":"screen"}'
    h2 = compute_event_hash(h1, {"action": "screen"}, t2)
    # Deliberately tamper with payload of e2 without altering h2
    tampered_p2 = '{"action":"screen","tampered_forgery":true}'
    e2 = MockAuditEvent(h1, h2, tampered_p2, "SCREEN", t2)

    res = AuditHashChain.verify_chain([e1, e2])
    assert res["status"] == "AUDIT_INTEGRITY_FAILURE"
    assert res["chain_valid"] is False
    assert res["failed_index"] == 1
