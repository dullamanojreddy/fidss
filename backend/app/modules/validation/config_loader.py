import json
import os
from typing import Dict, Any

_config_cache = None
DEFAULT_CONFIG = {
    "fuzzy_name_match_threshold": 85.0,
    "duplicate_identity_name_threshold": 85.0,
    "mrz_check_confidence": 0.95,
    "cross_validator_exact_mismatch_confidence": 0.9
}

def load_validation_config() -> Dict[str, Any]:
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config_path = os.path.join(os.path.dirname(__file__), "validation_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            file_config = json.load(f)
            # Merge with defaults
            _config_cache = {**DEFAULT_CONFIG, **file_config}
    except Exception:
        # Fallback to defaults on missing/malformed file
        _config_cache = DEFAULT_CONFIG.copy()

    return _config_cache
