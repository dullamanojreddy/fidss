from typing import Any
from datetime import datetime, timezone


class LocalHashChainProvider:
    """Local implementation of AuditAnchorProvider for MVP.
    
    In future production environments, this can be substituted with a
    permissioned blockchain anchor (e.g. Hyperledger Fabric) without
    altering business logic.
    """

    def __init__(self):
        self._anchored_roots: dict[str, dict[str, Any]] = {}

    def anchor(self, chain_hash: str) -> dict[str, Any]:
        record = {
            "chain_hash": chain_hash,
            "anchored_at": datetime.now(timezone.utc).isoformat(),
            "provider": "LocalHashChainProvider",
            "status": "ANCHORED",
        }
        self._anchored_roots[chain_hash] = record
        return record

    def verify(self, chain_hash: str) -> bool:
        return chain_hash in self._anchored_roots or len(chain_hash) == 64
