# FIDSS UI Specification Reference

This document formalizes the exact visual and behavioral specification of the FIDSS Web Interface based on the reference UI (`Screening Console`).

## 1. Visual Hierarchy & Color Palette
- **Background**: Modern clean light-slate `#F8FAFC` (`bg-slate-50`) with white elevated cards (`bg-white`).
- **Primary Color**: Deep Indigo / Royal Blue `#2563EB` (Tailwind `blue-600`) with hover `#1D4ED8`.
- **Status Accents**:
  - Clear / Success / Completed: Emerald Green `#10B981` (`text-emerald-600`, `bg-emerald-50`, `border-emerald-200`)
  - Warning / Review Recommended: Amber / Orange `#F59E0B` (`text-amber-600`, `bg-amber-50`, `border-amber-200`)
  - Critical / Mismatch / Tampered: Crimson Red `#EF4444` (`text-red-600`, `bg-red-50`, `border-red-200`)
  - Neutral / In Progress: Sky Blue `#0284C7` and Slate Gray `#64748B`.
- **Card Styling**: Rounded corners (`rounded-xl` or `rounded-2xl`), subtle hairline borders (`border border-slate-200`), soft shadow (`shadow-sm`).
- **Typography**: Clean sans-serif (`Inter`, `system-ui`). Bold headers (`font-bold text-slate-800`), crisp metadata labels (`text-xs text-slate-500 font-medium`), value text (`text-sm font-semibold text-slate-700`).

---

## 2. Shell Layout Components

### Left Sidebar (Width: ~260px)
- **Top Brand**:
  - Shield with checkmark icon in blue circle (`w-9 h-9 bg-blue-600 text-white rounded-lg flex items-center justify-center`).
  - Brand title: `FIDSS` (bold, 18px).
  - Subtitle: `Fake Identity & Document Screening System` (text-xs text-slate-400).
- **Navigation Links** (with active state indicator):
  - Dashboard
  - Screening Console (Active: highlighted pill with blue text, light blue background `bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600`)
  - Officer Review
  - Watchlist
  - Duplicate Identity
  - Documents
  - Audit Trail
  - Reports
  - System Settings
- **Bottom Officer Profile Card**:
  - Officer avatar photo / initials badge.
  - Name: `Inspector Arjun`
  - Subtitle: `Border Officer`
  - Presence badge: Green dot + `Online`
  - Logout action button with exit icon (`text-red-600 border border-red-200 rounded-md py-1 px-3 text-xs flex items-center gap-1 hover:bg-red-50`).

### Top Header Bar
- **Page Title**: `Screening Console` (h1, 22px, font-bold text-slate-900).
- **Subtitle**: `Real-time AI powered document analysis and risk assessment` (text-sm text-slate-500).
- **Header Actions (Right)**:
  - System Status: Green dot + `System Status: Operational` (pill with `bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1 rounded-full`).
  - Notification Bell icon with red count badge (`2`).
  - Officer Avatar with dropdown arrow.

---

## 3. Screening Console View Layout

### A. Stepper Workflow Indicator
A horizontal 7-step progress pipeline with connecting lines:
1. `Upload` (Completed or Active icon)
2. `OCR Extraction` (Checkmark icon)
3. `Validation & MRZ` (Checkmark icon)
4. `Tampering Analysis` (Checkmark icon)
5. `Face Verification` (Checkmark icon)
6. `Risk Assessment` (Active blue shield icon)
7. `Completed` (Pending gray icon)

### B. Metadata Summary Strip
Horizontal metadata bar with white background and border:
- `Screening ID`: e.g. `SID-2026-05-21-00124`
- `Document Type`: `Passport`
- `Nationality`: `IND (India)`
- `Submitted By`: `Inspector Arjun`
- `Submitted At`: `21 May 2026, 09:15 AM`
- `Status`: `In Progress` (blue badge)
- `Action`: "Download Report" button (with download icon)

### C. 3-Column Core Screening Grid
- **Column 1: Document Preview & Key Findings**
  - **Document Preview Card**:
    - Image container showing the passport/ID document with crisp resolution.
    - Floating / bottom action toolbar: `Zoom In`, `Zoom Out`, `View Original`.
  - **Key Findings (Evidence) Card**:
    - Header: `Key Findings (Evidence)`
    - List of bulleted findings with category/severity badges (`INFO`, `WARNING`, `CRITICAL`):
      - "MRZ checksum verification passed" [INFO]
      - "All extracted fields are valid and consistent" [INFO]
      - "No tampering artifacts detected" [INFO]
      - "Face match score: 92.4%" [INFO]
    - Link: `View Full Evidence List ->`

- **Column 2: Overall Risk Assessment & Extracted Information**
  - **Overall Risk Assessment Card**:
    - Big green shield with checkmark badge.
    - Large title: `CLEAR` / `Low Risk`.
    - Risk Score: `18 / 100` (bold, large font).
    - Horizontal gradient slider bar (green -> yellow -> red) with position indicator at 18%.
    - Description: *"This document has passed all verification checks and no significant risk factors were detected."*
    - Footer tag: `Screening Level` -> `CLEAR` badge.
  - **Document Information (Extracted) Card**:
    - 2-column icon-grid of extracted fields:
      - Passport Number: `R1234567`
      - Date of Expiry: `14/07/2030`
      - Nationality: `INDIAN`
      - Gender: `M`
      - Date of Birth: `12/08/1990`
      - Place of Birth: `NEW DELHI`
      - Date of Issue: `15/07/2020`
      - Document Type: `Passport`

- **Column 3: Module Results & Next Step**
  - **Module Results Card**:
    - OCR Extraction: `Completed` (green check)
    - Validation & MRZ: `Completed` (green check)
    - Tampering Analysis: `Completed` (green check)
    - Face Verification: `Match (92.4%)` (green check)
    - Risk Assessment: `Completed` (green check)
    - Link: `View All Evidence (23) ->`
  - **Next Step Card**:
    - Clipboard icon graphic.
    - Text: *"Proceed to Officer Review for final decision and notes."*
    - Primary Button: `Proceed to Review ->` (royal blue button with arrow).

### D. Bottom Section: Recent Screenings Table
- Table Header: `Recent Screenings`, with right link `View All Screenings ->`.
- Columns:
  1. Screening ID (e.g. `SID-2026-05-21-00123`)
  2. Document Type (`Visa`, `Passport`)
  3. Submitted At (`21 May 2026, 09:08 AM`)
  4. Risk Level (`REVIEW RECOMMENDED` in orange badge, `CLEAR` in green)
  5. Risk Score (`45 / 100`)
  6. Status (`Completed` green badge)
  7. Action (View Eye icon, Download icon, More dots)

---

## 4. Other Core Pages
- **Officer Review Page**: Side-by-side evidence inspection, review decision buttons (`ACCEPT`, `REJECT`, `ESCALATE`, `REQUEST_RECAPTURE`, `MARK_INCONCLUSIVE`), officer reason code, notes text area, and audit submission.
- **Audit Trail & Integrity View**: Chronological block timeline showing `block_index`, `timestamp`, `event_type`, `previous_hash`, and `current_hash`. Real-time `Verify Audit Integrity` action and `Simulate Audit Tampering` demo toggle.
- **Dashboard**: High-level KPI metric cards (Total Screenings, Clear Rate, Flagged, Average Processing Time), risk distribution chart, and module status health.
- **System Settings (Admin)**: Threshold sliders (Face similarity threshold, MRZ strictness, Tamper sensitivity), provider toggle, model registry table.
