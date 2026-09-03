# FIDSS — Fake Identity & Document Screening System
**SIH 2026 — Problem Statement 26188 (Blockchain & Cybersecurity / Smart Border Security)**

FIDSS is an explainable, multi-layered identity document screening and decision-support platform designed for border checkpoints. It fuses classical computer-vision forensics, OCR extraction, ICAO 9303 MRZ validation, face biometrics, and a tamper-evident SHA-256 hash chain into a unified screening console.

---

## Architecture & Person 5 Scope

This implementation strictly implements **Person 5 (Platform, Backend, Orchestrator & Frontend Shell)**:
- **Shared Pydantic Schemas (`backend/app/schemas/`)**: Pure contract boundaries for all 5 roles.
- **Relational Database (`backend/app/models/`, `backend/app/db/`)**: 100% database-driven architecture using SQLAlchemy with MySQL 8 (production) and SQLite (demo/dev). Zero static mock data.
- **Screening Orchestrator (`backend/app/services/orchestrator.py`)**: Explicit 12-step pipeline with `ModuleDispatcher` abstraction and failure isolation (module failures never yield silent CLEAR).
- **Cryptographic Audit Trail (`backend/app/services/audit/`)**: SHA-256 previous-hash chained canonical event ledger with automated tamper detection and `AuditAnchorProvider` abstraction.
- **FastAPI REST API (`backend/app/api/`)**: Authentication, Screenings, Documents, Officer Review workflow, Audit Verification, Watchlist, Dashboard, and System Settings.
- **React 18 + TailwindCSS Frontend (`frontend/`)**: Modern UI faithfully recreating the Screening Console specification, with Stepper, Document Preview, Risk Assessment Gauge, Module Results, Extracted Information, Officer Review, and Audit Verification.

> **Ownership Boundary**: Persons 1–4 modules (`ocr/`, `quality/`, `validation/`, `tampering/`, `face/`, `fusion/` and their respective prototype components) remain unedited and isolated.

---

## Quick Start & Running Commands

### 1. Prerequisites
- **Python**: 3.11+ (Tested on Python 3.14)
- **Node.js**: v18+ (Tested on Node.js v24)
- **Database**: MySQL 8 or SQLite (configured via `.env`)

---

### 2. Backend Setup & Execution

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run automated unit, contract, and integration tests
python -m pytest tests/ -v

# Start FastAPI backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Backend API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

### 3. Frontend Setup & Execution

```powershell
# Open a new terminal and navigate to frontend directory
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```
- Access the Web Application at: `http://localhost:5173`

---

### 4. Docker Compose (Full Stack with MySQL 8)

To launch the complete production-style environment with MySQL 8, FastAPI, and Frontend:
```powershell
docker compose up --build
```

---

## Default Credentials & Demo Roles
Driven strictly by environment variables (see `.env.example`):
- **Border Officer**: `arjun` / `OfficerArjun2026!`
- **Administrator**: `admin` / `AdminSecure2026!`

---

## Demonstration Script (SIH Presentation)
1. **Login**: Sign in as `arjun`.
2. **Screening Console**:
   - Inspect active session `SID-2026-05-21-00124`.
   - Observe the 7-step pipeline indicator, Document Preview, Extracted Fields, and Risk Score (18 / 100, CLEAR).
   - Test "New Screening" by uploading any passport or identity image.
3. **Officer Review**:
   - Click "Proceed to Review". Select decision (`ACCEPT`), reason, and enter justification notes. Submit to append an audited event.
4. **Cryptographic Audit Verification**:
   - Navigate to "Audit Trail".
   - Click **"Verify Audit Integrity"** $\to$ observe Green **VERIFIED** status.
   - Click **"Simulate Row Tampering (Demo)"** $\to$ re-verify $\to$ observe immediate Red **AUDIT INTEGRITY FAILURE**, demonstrating tamper evidence.
