"""Configurable, explainable evidence fusion with strict failure invariants."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from app.schemas.module_result import ModuleResult
from app.schemas.quality_result import QualityResult

CONFIG_PATH = Path(__file__).with_name("fusion_config.yaml")

@dataclass(frozen=True)
class FusionResult:
    risk_score: float
    screening_level: str
    recommendation: str
    contributions: tuple[dict, ...]
    incomplete_modules: tuple[str, ...]

def load_config(path: str | Path = CONFIG_PATH) -> dict:
    with Path(path).open("r",encoding="utf-8") as stream:
        config = json.load(stream)
    required = {"severity_points","module_weights","thresholds","inconclusive_score_floor"}
    if not required.issubset(config):
        raise ValueError("Fusion configuration is incomplete")
    return config

def fuse(quality: QualityResult, module_results: list[ModuleResult], config: dict | None = None) -> FusionResult:
    config = config or load_config()
    if quality.status == "FAIL":
        return FusionResult(85.0,"INCONCLUSIVE","Image quality failed. Recapture required.",(),("quality",))
    contributions = []
    total = 0.0
    for result in module_results:
        module_weight = float(config["module_weights"].get(result.module,1.0))
        for item in result.evidence_items:
            base = float(config["severity_points"].get(item.severity,0.0))
            category_weight = float(config.get("category_weights",{}).get(item.category,1.0))
            points = base * module_weight * category_weight * item.confidence
            total += points
            contributions.append({"evidence_id":str(item.id),"module":result.module,"category":item.category,"severity":item.severity,"confidence":round(item.confidence,4),"points":round(points,2)})
    score = round(min(100.0,max(0.0,total)),1)
    incomplete = tuple(result.module for result in module_results if result.status in {"FAILED","INCONCLUSIVE"})
    if not module_results:
        incomplete = ("all_checks",)
    if incomplete:
        score = max(score,float(config["inconclusive_score_floor"]))
        return FusionResult(round(score,1),"REVIEW_RECOMMENDED",f"Checks failed or were inconclusive for: {', '.join(incomplete)}. Officer review required.",tuple(contributions),incomplete)
    thresholds = config["thresholds"]
    if score <= float(thresholds["clear_max"]):
        level, recommendation = "CLEAR", "All completed checks passed without significant risk signals."
    elif score <= float(thresholds["review_max"]):
        level, recommendation = "REVIEW_RECOMMENDED", "Low to moderate anomalies detected. Officer review recommended."
    elif score <= float(thresholds["enhanced_review_max"]):
        level, recommendation = "ENHANCED_REVIEW_RECOMMENDED", "Elevated risk signals detected. Enhanced inspection recommended."
    else:
        level, recommendation = "INCONCLUSIVE", "High or contradictory risk evidence requires escalation."
    return FusionResult(score,level,recommendation,tuple(contributions),())

def calculate_risk(quality: QualityResult, module_results: list[ModuleResult]) -> tuple[float,str,str]:
    result = fuse(quality,module_results)
    return result.risk_score,result.screening_level,result.recommendation
