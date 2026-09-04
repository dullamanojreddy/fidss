# Evidence fusion contract

`fuse(quality: QualityResult, module_results: list[ModuleResult]) -> FusionResult` scores only observed evidence. Every contribution records its module, category, severity, confidence, and points. Weights and level thresholds live in `fusion_config.yaml` (JSON syntax, which is valid YAML).

Quality failure returns `INCONCLUSIVE`. A failed/inconclusive module or an empty result list can never return `CLEAR`; it applies the configured review floor and requires officer review. `calculate_risk(...)` provides the tuple expected by the platform integration layer.
