import json
import uuid
from datetime import datetime, timezone
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.screening import Screening
from app.models.document import Document
from app.models.document_field import DocumentField
from app.models.module_result import ModuleResultModel
from app.models.evidence_item import EvidenceItemModel
from app.schemas.document_context import DocumentContext
from app.schemas.quality_result import QualityResult
from app.schemas.module_result import ModuleResult
from app.schemas.screening_result import ScreeningResultResponse
from app.services.upload.upload_service import UploadService
from app.services.module_dispatcher import ModuleDispatcher
from app.services.audit.audit_service import AuditService


class ScreeningOrchestrator:
    """Executes the explicit 12-step screening pipeline.
    
    Step 01: Receive upload
    Step 02: Validate file
    Step 03: Compute SHA-256
    Step 04: Store document
    Step 05: Determine document type
    Step 06: Run image quality assessment
    Step 07: OCR extraction & field normalization
    Step 08: Document/MRZ validation & watchlist check
    Step 09: Tampering & forensic CV analysis
    Step 10: Face verification
    Step 11: Evidence aggregation & risk fusion
    Step 12: Persist results & cryptographic audit logging
    """

    @staticmethod
    async def execute_screening(
        db: Session,
        document_file: UploadFile,
        selfie_file: UploadFile | None = None,
        document_type: str = "passport",
        officer_id: str | None = None,
    ) -> ScreeningResultResponse:
        screening_id = str(uuid.uuid4())
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        random_suffix = str(uuid.uuid4())[:5].upper()
        screening_number = f"SID-{today_str}-{random_suffix}"

        # ----------------------------------------------------------------------
        # Step 01-04: Upload, Validate, Compute SHA-256, Store Document
        # ----------------------------------------------------------------------
        doc_upload = await UploadService.validate_and_save(document_file)
        document_id = str(uuid.uuid4())

        selfie_upload = None
        if selfie_file:
            selfie_upload = await UploadService.validate_and_save(selfie_file)

        # ----------------------------------------------------------------------
        # Step 05: Determine document type & construct context
        # ----------------------------------------------------------------------
        context = DocumentContext(
            screening_id=uuid.UUID(screening_id),
            document_id=uuid.UUID(document_id),
            image_path=doc_upload["storage_path"],
            document_type=document_type,
            image_sha256=doc_upload["sha256_hash"],
            selfie_path=selfie_upload["storage_path"] if selfie_upload else None,
        )

        # ----------------------------------------------------------------------
        # Step 06: Run Image Quality Assessment
        # ----------------------------------------------------------------------
        quality_res: QualityResult = ModuleDispatcher.run_quality(context)
        context.quality_result = quality_res

        # If quality gate fails severely, mark inconclusive early
        early_abort = quality_res.status == "FAIL"

        module_results: list[ModuleResult] = []
        extracted_fields: dict[str, str] = {}

        if not early_abort:
            # ------------------------------------------------------------------
            # Step 07: OCR Extraction
            # ------------------------------------------------------------------
            ocr_mod_res, extracted = ModuleDispatcher.run_ocr(context)
            module_results.append(ocr_mod_res)
            extracted_fields.update(extracted)
            context.ocr_result = ocr_mod_res.metadata

            # ------------------------------------------------------------------
            # Step 08: Document / MRZ Validation & Duplicate Identity Check
            # ------------------------------------------------------------------
            historical_records = []
            try:
                past_fields = db.query(DocumentField).all()
                screenings_map: dict[str, dict[str, str]] = {}
                for pf in past_fields:
                    if pf.screening_id != screening_id:
                        screenings_map.setdefault(pf.screening_id, {})[pf.field_name] = pf.field_value
                for s_id, fields in screenings_map.items():
                    historical_records.append({"screening_id": s_id, **fields})
            except Exception:
                historical_records = []

            context.allowed_outputs["historical_records"] = historical_records

            val_mod_res = ModuleDispatcher.run_validation(context)
            module_results.append(val_mod_res)
            context.validation_result = val_mod_res.metadata

            # ------------------------------------------------------------------
            # Step 09: Tampering & Forensic Analysis
            # ------------------------------------------------------------------
            tamper_mod_res = ModuleDispatcher.run_tampering(context)
            module_results.append(tamper_mod_res)

            # ------------------------------------------------------------------
            # Step 10: Face Verification
            # ------------------------------------------------------------------
            face_mod_res = ModuleDispatcher.run_face(context)
            module_results.append(face_mod_res)

        # ----------------------------------------------------------------------
        # Step 11: Evidence Aggregation & Risk Fusion
        # ----------------------------------------------------------------------
        risk_score, screening_level, recommendation = ModuleDispatcher.run_fusion(
            context, quality_res, module_results
        )

        # ----------------------------------------------------------------------
        # Step 12: Database Persistence & Cryptographic Audit Logging
        # ----------------------------------------------------------------------
        nationality = extracted_fields.get("Nationality", "IND (India)")
        now = datetime.now(timezone.utc)

        # 1. Create Screening Master record
        screening = Screening(
            id=screening_id,
            screening_number=screening_number,
            status="COMPLETED",
            document_type=document_type,
            nationality=nationality,
            overall_risk_score=risk_score,
            screening_level=screening_level,
            recommendation_text=recommendation,
            created_by=officer_id,
            created_at=now,
            completed_at=now,
        )
        db.add(screening)

        # 2. Create Document record
        doc_record = Document(
            id=document_id,
            screening_id=screening_id,
            original_filename=doc_upload["original_filename"],
            storage_path=doc_upload["storage_path"],
            file_size=doc_upload["file_size"],
            mime_type=doc_upload["mime_type"],
            sha256_hash=doc_upload["sha256_hash"],
            document_type=document_type,
            selfie_path=selfie_upload["storage_path"] if selfie_upload else None,
            created_at=now,
        )
        db.add(doc_record)

        # 3. Create Document Fields
        for k, v in extracted_fields.items():
            field_rec = DocumentField(
                id=str(uuid.uuid4()),
                screening_id=screening_id,
                field_name=k,
                field_value=str(v),
                confidence=0.98,
                source="OCR",
                created_at=now,
            )
            db.add(field_rec)

        # 4. Create Module Results & Evidence Items with Provenance
        all_evidence_schemas = []
        for mod_res in module_results:
            mod_model = ModuleResultModel(
                id=str(mod_res.id),
                screening_id=screening_id,
                module_name=mod_res.module,
                status=mod_res.status,
                processing_time_ms=mod_res.processing_time_ms or 0,
                errors_json=json.dumps(mod_res.errors),
                metadata_json=json.dumps(mod_res.metadata),
                created_at=now,
            )
            db.add(mod_model)

            for ev in mod_res.evidence_items:
                all_evidence_schemas.append(ev)
                ev_model = EvidenceItemModel(
                    id=str(ev.id),
                    screening_id=screening_id,
                    module_result_id=str(mod_res.id),
                    module_name=mod_res.module,
                    category=ev.category,
                    severity=ev.severity,
                    source=ev.source,
                    confidence=ev.confidence,
                    description=ev.description,
                    region_json=json.dumps(ev.document_region.model_dump()) if ev.document_region else None,
                    metrics_json=json.dumps(ev.metrics),
                    created_at=now,
                )
                db.add(ev_model)

        db.commit()

        # 5. Append Canonical Event to SHA-256 Audit Chain
        AuditService.log_event(
            db=db,
            event_type="SCREENING_CREATED",
            event_payload={
                "screening_id": screening_id,
                "screening_number": screening_number,
                "document_sha256": doc_upload["sha256_hash"],
                "risk_score": risk_score,
                "screening_level": screening_level,
                "module_count": len(module_results),
                "evidence_count": len(all_evidence_schemas),
            },
            screening_id=screening_id,
            actor_id=officer_id or "system",
        )

        return ScreeningResultResponse(
            id=uuid.UUID(screening_id),
            screening_number=screening_number,
            status="COMPLETED",
            document_type=document_type,
            nationality=nationality,
            overall_risk_score=risk_score,
            screening_level=screening_level,
            recommendation_text=recommendation,
            document_id=uuid.UUID(document_id),
            document_preview_url=f"/api/documents/{document_id}/file",
            submitted_by="Inspector Arjun",
            submitted_at=now,
            completed_at=now,
            extracted_fields=extracted_fields,
            module_results=module_results,
            key_findings=all_evidence_schemas[:4],
            total_evidence_count=len(all_evidence_schemas),
            current_step=7,
        )
