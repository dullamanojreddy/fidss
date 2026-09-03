import json
import hashlib
from datetime import datetime
from typing import Any


def canonical_json(data: Any) -> str:
    """Serialize data to a deterministic, canonical JSON string."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def format_timestamp(timestamp: datetime | str) -> str:
    if isinstance(timestamp, str):
        return timestamp
    # Format deterministically to second resolution
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def compute_event_hash(previous_hash: str | None, payload: dict, timestamp: datetime | str) -> str:
    """Compute SHA-256 hash chaining previous_hash, canonical payload and deterministic timestamp."""
    prev_str = previous_hash if previous_hash else "GENESIS_ROOT"
    time_str = format_timestamp(timestamp)
    canonical_payload = canonical_json(payload)
    
    combined = f"{prev_str}:{canonical_payload}:{time_str}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


class AuditHashChain:
    @staticmethod
    def verify_chain(events: list[Any], is_subchain: bool = False) -> dict:
        """Verify the integrity of a sequence of audit log entries.
        
        Returns dict with status ('VERIFIED' or 'AUDIT_INTEGRITY_FAILURE'),
        details, and broken block index if invalid.
        """
        if not events:
            return {
                "status": "VERIFIED",
                "total_events": 0,
                "chain_valid": True,
                "message": "Audit chain is empty and valid.",
            }

        expected_prev_hash: str | None = None

        for index, event in enumerate(events):
            if index == 0:
                if not is_subchain:
                    if event.previous_hash is not None and event.previous_hash != "GENESIS_ROOT":
                        return {
                            "status": "AUDIT_INTEGRITY_FAILURE",
                            "total_events": len(events),
                            "chain_valid": False,
                            "failed_index": 0,
                            "message": f"Genesis block contains invalid previous_hash '{event.previous_hash}'.",
                        }
            else:
                if event.previous_hash != expected_prev_hash:
                    return {
                        "status": "AUDIT_INTEGRITY_FAILURE",
                        "total_events": len(events),
                        "chain_valid": False,
                        "failed_index": index,
                        "message": (
                            f"Broken chain link at block {index}: expected previous_hash "
                            f"'{expected_prev_hash}' but found '{event.previous_hash}'."
                        ),
                    }

            # Recalculate current hash
            try:
                payload = json.loads(event.event_payload_json)
            except Exception:
                payload = event.event_payload_json

            recalculated_hash = compute_event_hash(
                event.previous_hash, payload, event.timestamp
            )

            if recalculated_hash != event.current_hash:
                return {
                    "status": "AUDIT_INTEGRITY_FAILURE",
                    "total_events": len(events),
                    "chain_valid": False,
                    "failed_index": index,
                    "message": (
                        f"Tamper detected at block {index} ({event.event_type}): "
                        f"recalculated hash '{recalculated_hash[:16]}...' "
                        f"does not match recorded hash '{event.current_hash[:16]}...'."
                    ),
                }

            expected_prev_hash = event.current_hash

        return {
            "status": "VERIFIED",
            "total_events": len(events),
            "chain_valid": True,
            "head_hash": expected_prev_hash,
            "message": "Cryptographic hash chain verified successfully. Zero discrepancies detected.",
        }
