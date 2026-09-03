from typing import Protocol, runtime_checkable, Any


@runtime_checkable
class AuditAnchorProvider(Protocol):
    def anchor(self, chain_hash: str) -> dict[str, Any]:
        """Anchor state or chain hash to persistent/distributed store."""
        ...

    def verify(self, chain_hash: str) -> bool:
        """Verify chain hash against anchored reference."""
        ...
