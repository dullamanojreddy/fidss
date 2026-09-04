import time
from typing import Dict, Any
from .config_loader import load_validation_config

from app.schemas.document_context import DocumentContext
from app.schemas.module_result import ModuleResult
from app.schemas.evidence_item import EvidenceItem
from .mrz_detector import detect_mrz
from .mrz_parser import parse_mrz
from .rule_engine import validate_document, RuleEngineError
from .cross_validator import cross_validate
from .watchlist import check_watchlist
from app.providers.watchlist.local_provider import LocalSyntheticWatchlistProvider
from .duplicate_identity import check_duplicate_identity


def analyze(context: DocumentContext) -> ModuleResult:
    start_time = time.time()
    errors = []
    evidence_items = []
    
    # Metadata for debugging / demo
    metadata = {
        "mrz_checks_run": False,
        "rule_engine_run": False,
        "cross_validation_run": False,
        "watchlist_run": False,
        "duplicate_identity_run": False
    }
    
    step_failures = 0

    try:
        ocr_fields = context.ocr_result or {}
        
        # 3. MRZ Pipeline
        mrz_parsed_fields = {}
        try:
            raw_lines = ocr_fields.get("raw_lines", [])
            mrz_lines = detect_mrz(raw_lines)
            
            if mrz_lines:
                metadata["mrz_checks_run"] = True
                mrz_result = parse_mrz(mrz_lines)
                
                if mrz_result.mrz_type != "UNKNOWN":
                    mrz_dict = mrz_result.model_dump()
                    
                    for field_name, field_status in mrz_dict.items():
                        if isinstance(field_status, dict) and "status" in field_status:
                            if field_status["status"] == "INVALID":
                                evidence_items.append(EvidenceItem(
                                    screening_id=context.screening_id,
                                    module_name="validation",
                                    category="MRZ_CHECK_FAILED",
                                    severity="HIGH",
                                    source="mrz_checksum",
                                    confidence=load_validation_config()["mrz_check_confidence"],
                                    description=f"Invalid check digit or format for field: {field_name}"
                                ))
                            elif field_status["status"] == "INCOMPLETE":
                                evidence_items.append(EvidenceItem(
                                    screening_id=context.screening_id,
                                    module_name="validation",
                                    category="MRZ_CHECK_FAILED",
                                    severity="MEDIUM",
                                    source="mrz_checksum",
                                    confidence=load_validation_config()["mrz_check_confidence"],
                                    description=f"Incomplete or malformed field: {field_name}"
                                ))
                                
                    if mrz_dict.get("composite_status") == "INVALID":
                        evidence_items.append(EvidenceItem(
                            screening_id=context.screening_id,
                            module_name="validation",
                            category="MRZ_CHECK_FAILED",
                            severity="HIGH",
                            source="mrz_checksum",
                            confidence=load_validation_config()["mrz_check_confidence"],
                            description="Composite check digit is invalid"
                        ))
                    elif mrz_dict.get("composite_status") == "INCOMPLETE":
                        evidence_items.append(EvidenceItem(
                            screening_id=context.screening_id,
                            module_name="validation",
                            category="MRZ_CHECK_FAILED",
                            severity="MEDIUM",
                            source="mrz_checksum",
                            confidence=load_validation_config()["mrz_check_confidence"],
                            description="Composite check digit is incomplete"
                        ))

                    for k, v in mrz_dict.items():
                        if isinstance(v, dict) and "value" in v:
                            mrz_parsed_fields[k] = v["value"]

        except Exception as e:
            metadata["mrz_checks_run"] = False
            step_failures += 1
            err_msg = f"validation sub-check 'mrz_pipeline' failed: {str(e)}"
            errors.append(err_msg)
            evidence_items.append(EvidenceItem(
                screening_id=context.screening_id,
                module_name="validation",
                category="MODULE_STEP_FAILED",
                severity="MEDIUM",
                source="mrz_pipeline",
                confidence=0.0,
                description=err_msg
            ))

        # 4. Rule Engine
        try:
            findings = validate_document(ocr_fields, context.document_type, country="IND")
            metadata["rule_engine_run"] = True
            for f in findings:
                if f.get("category") == "system" and "No rules file found" in f.get("description", ""):
                    # Normally shouldn't happen unless caught explicitly via Exception, but keeping for compatibility
                    evidence_items.append(EvidenceItem(
                        screening_id=context.screening_id,
                        module_name="validation",
                        category="RULES_UNAVAILABLE",
                        severity="LOW",
                        source="rule_engine",
                        confidence=1.0,
                        description=f.get("description", "")
                    ))
                else:
                    evidence_items.append(EvidenceItem(
                        screening_id=context.screening_id,
                        module_name="validation",
                        category=f.get("category", "RULE_VALIDATION_FAILED"),
                        severity=f.get("severity", "MEDIUM"),
                        source="rule_engine",
                        confidence=1.0,
                        description=f.get("description", ""),
                        metrics={"fields": ", ".join(f.get("fields", []))}
                    ))
        except RuleEngineError as e:
            metadata["rule_engine_run"] = False
            step_failures += 1
            evidence_items.append(EvidenceItem(
                screening_id=context.screening_id,
                module_name="validation",
                category="RULES_UNAVAILABLE",
                severity="LOW",
                source="rule_engine",
                confidence=1.0,
                description=f"Rules unavailable for this document type: {str(e)}"
            ))
        except Exception as e:
            metadata["rule_engine_run"] = False
            step_failures += 1
            err_msg = f"validation sub-check 'rule_engine' failed: {str(e)}"
            errors.append(err_msg)
            evidence_items.append(EvidenceItem(
                screening_id=context.screening_id,
                module_name="validation",
                category="MODULE_STEP_FAILED",
                severity="MEDIUM",
                source="rule_engine",
                confidence=0.0,
                description=err_msg
            ))

        # 5. Cross Validation
        try:
            if metadata["mrz_checks_run"]:
                cv_findings = cross_validate(ocr_fields, mrz_parsed_fields)
                metadata["cross_validation_run"] = True
                for f in cv_findings:
                    evidence_items.append(EvidenceItem(
                        screening_id=context.screening_id,
                        module_name="validation",
                        **f
                    ))
        except Exception as e:
            metadata["cross_validation_run"] = False
            step_failures += 1
            err_msg = f"validation sub-check 'cross_validation' failed: {str(e)}"
            errors.append(err_msg)
            evidence_items.append(EvidenceItem(
                screening_id=context.screening_id,
                module_name="validation",
                category="MODULE_STEP_FAILED",
                severity="MEDIUM",
                source="cross_validation",
                confidence=0.0,
                description=err_msg
            ))

        # 6. Watchlist
        try:
            provider = context.allowed_outputs.get("watchlist_provider")
            if not provider:
                provider = LocalSyntheticWatchlistProvider()
                
            doc_num = ocr_fields.get("document_number")
            name = ocr_fields.get("name")
            if not name:
                surname = ocr_fields.get("surname", "")
                given = ocr_fields.get("given_names", "")
                name = f"{surname} {given}".strip()
            dob = ocr_fields.get("date_of_birth")
            
            wl_findings = check_watchlist(doc_num, name, dob, provider)
            metadata["watchlist_run"] = True
            for f in wl_findings:
                evidence_items.append(EvidenceItem(
                    screening_id=context.screening_id,
                    module_name="validation",
                    **f
                ))
        except Exception as e:
            metadata["watchlist_run"] = False
            step_failures += 1
            err_msg = f"validation sub-check 'watchlist' failed: {str(e)}"
            errors.append(err_msg)
            evidence_items.append(EvidenceItem(
                screening_id=context.screening_id,
                module_name="validation",
                category="MODULE_STEP_FAILED",
                severity="MEDIUM",
                source="watchlist",
                confidence=0.0,
                description=err_msg
            ))

        # 7. Duplicate Identity
        try:
            historical_records = context.allowed_outputs.get("historical_records", [])
            current_record = dict(ocr_fields)
            current_record["screening_id"] = str(context.screening_id)
            # Recompute name for consistency if it was built
            name = ocr_fields.get("name")
            if not name:
                surname = ocr_fields.get("surname", "")
                given = ocr_fields.get("given_names", "")
                name = f"{surname} {given}".strip()
            current_record["name"] = name
            
            dup_findings = check_duplicate_identity(current_record, historical_records)
            metadata["duplicate_identity_run"] = True
            for f in dup_findings:
                evidence_items.append(EvidenceItem(
                    screening_id=context.screening_id,
                    module_name="validation",
                    **f
                ))
        except Exception as e:
            metadata["duplicate_identity_run"] = False
            step_failures += 1
            err_msg = f"validation sub-check 'duplicate_identity' failed: {str(e)}"
            errors.append(err_msg)
            evidence_items.append(EvidenceItem(
                screening_id=context.screening_id,
                module_name="validation",
                category="MODULE_STEP_FAILED",
                severity="MEDIUM",
                source="duplicate_identity",
                confidence=0.0,
                description=err_msg
            ))

        if not context.ocr_result:
            status = "PARTIAL"
        elif step_failures > 0:
            status = "PARTIAL"
        else:
            status = "SUCCESS"

    except Exception as e:
        status = "FAILED"
        errors.append(f"Catastrophic failure in analyze: {str(e)}")
        evidence_items = []

    processing_time_ms = int((time.time() - start_time) * 1000)

    return ModuleResult(
        module="validation",
        status=status,
        evidence_items=evidence_items,
        processing_time_ms=processing_time_ms,
        errors=errors,
        metadata=metadata
    )
