import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List

RULES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'rules')
_rules_cache = {}

class RuleEngineError(Exception):
    pass

def load_rules(document_type: str, country: str = "IND") -> Dict[str, Any]:
    cache_key = f"{document_type}_{country}"
    if cache_key in _rules_cache:
        return _rules_cache[cache_key]
        
    rule_path = os.path.join(RULES_DIR, document_type, f"{country}.json")
    if not os.path.exists(rule_path):
        raise RuleEngineError(f"No rules file found for document_type='{document_type}', country='{country}'")
        
    with open(rule_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
        _rules_cache[cache_key] = rules
        return rules

def _parse_date(date_str: str) -> datetime:
    # Handle YYYY-MM-DD or YYMMDD commonly output by OCR or normalization
    # Assume ISO format YYYY-MM-DD as per constraint "ISO date strings"
    if not date_str:
        return None
    try:
        # ISO format YYYY-MM-DD
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        try:
            # Fallback for YYMMDD
            return datetime.strptime(date_str, "%y%m%d")
        except ValueError:
            return None

def validate_document(fields: Dict[str, str], document_type: str, country: str = "IND") -> List[Dict[str, Any]]:
    findings = []
    
    try:
        rules = load_rules(document_type, country)
    except RuleEngineError as e:
        findings.append({
            "category": "system",
            "severity": "CRITICAL",
            "description": str(e),
            "fields": []
        })
        return findings

    # 1. Required field presence check
    for req_field in rules.get("required_fields", []):
        if req_field not in fields or not fields[req_field]:
            findings.append({
                "category": "validation",
                "severity": "HIGH",
                "description": f"Missing required field: {req_field}",
                "fields": [req_field]
            })

    # 2. Date ordering checks
    for rule in rules.get("date_order_rules", []):
        before_field = rule.get("before_field")
        after_field = rule.get("after_field")
        rule_desc = rule.get("rule", f"{before_field} must precede {after_field}")
        
        before_val = fields.get(before_field)
        after_val = fields.get(after_field)
        
        if before_val and after_val:
            d_before = _parse_date(before_val)
            d_after = _parse_date(after_val)
            if d_before and d_after:
                if d_before > d_after:
                    findings.append({
                        "category": "validation",
                        "severity": "MEDIUM",
                        "description": f"Date order mismatch: {rule_desc}",
                        "fields": [before_field, after_field]
                    })

    # 3. Expiry status
    expiry_thresholds = rules.get("expiry_thresholds_days", {})
    if expiry_thresholds and "date_of_expiry" in fields and fields["date_of_expiry"]:
        d_expiry = _parse_date(fields["date_of_expiry"])
        if d_expiry:
            now = datetime.now()
            days_to_expiry = (d_expiry - now).days
            
            if days_to_expiry < 0:
                findings.append({
                    "category": "validation",
                    "severity": "CRITICAL",
                    "description": "Document is EXPIRED",
                    "fields": ["date_of_expiry"]
                })
            elif "expiring_soon" in expiry_thresholds and days_to_expiry <= expiry_thresholds["expiring_soon"]:
                findings.append({
                    "category": "validation",
                    "severity": "MEDIUM",
                    "description": f"Document is EXPIRING_SOON (in {days_to_expiry} days)",
                    "fields": ["date_of_expiry"]
                })

    # 4. Document number pattern match
    pattern = rules.get("document_number_pattern")
    doc_number = fields.get("document_number")
    if pattern and doc_number:
        if not re.match(pattern, doc_number):
            findings.append({
                "category": "validation",
                "severity": "MEDIUM",
                "description": f"Document number does not match expected pattern for {country} {document_type}",
                "fields": ["document_number"]
            })
            
    return findings
