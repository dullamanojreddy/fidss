# FIDSS Testing Strategy

## 1. Test Layers
- **Contract Tests (`tests/contract/`)**: Validate that all modules (P1–P4) strictly respect the Pydantic schemas defined in `app/schemas/`.
- **Unit Tests (`tests/unit/`)**: Validate individual services: upload validation, SHA-256 computation, hash chain calculation, and RBAC token generation.
- **Integration Tests (`tests/integration/`)**: Test end-to-end flows: uploading a document, executing the 12-step orchestrator, persisting results, submitting an officer review, and auditing verification.

## 2. Test Commands
```bash
# Run all tests
pytest tests/ -v

# Run contract tests
pytest tests/contract/ -v

# Run integration tests
pytest tests/integration/ -v
```
