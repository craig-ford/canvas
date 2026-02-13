Below is a **very brief, build-ready specification** for a small web app
that implements the **Portfolio Dashboard** plus **individual VBU
pages**, aligned to your **Strategy Implementation Methodology** (Intent
→ Theses → Proof Points → Monthly loop) and the **Strategy + Lifecycle
Canvas**.

## 1) Goal

Create a lightweight web app that:

- Lets each GM maintain a single "living" **Strategy + Lifecycle
  Canvas** per product/VBU.
- Rolls those up into a **Portfolio Dashboard** so you (and the GMs) can
  see: lifecycle lanes, what's being tested next, proof points due,
  constraints, and whether evidence is moving.

The app should strongly privilege **evidence over activity** and make
the monthly review loop easy to run.

## 2) Core concepts (data to capture)

Each VBU/Product has one Canvas with the following fields:

### A) Context

- VBU / Company
- Product / Product Group
- **Lifecycle Lane**: Build / Sell / Milk / Reframe
- "In this lane, success over the next 12--24 months means..." (one
  sentence)

### B) Future State Intent (3--5 years)

- Free-text statement (prompted by: "It's 20XX... what is now true?")

### C) Strategic Theses (12--36 months)

- 3--5 theses (each: short text, phrased as "new normal", not a project)

### D) Lifecycle Implications (discipline / guardrails)

- Primary focus in this lane (Learning / Replication / Cash & Risk)
- "What we must resist doing"
- "What good discipline looks like"

### E) Proof Points (3--6 months)

- For each thesis: 0--n proof points (observable signals, not
  activities)

- Each proof point should support:

  - status: Not started / In progress / Observed / Stalled
  - optional "evidence note" + link/file reference
  - optional "target review month"

### F) Primary Constraint / Risk

- Single biggest blocker to the next proof point

### G) Cadence commitments (next monthly review)

- 1--3 commitments before next check-in
- "At the next review, we are primarily testing..." (select a thesis or
  proof point)

### H) Monthly review prompts (repeatable template)

Store monthly review entries answering: what moved (evidence), what
changed beliefs, what threatens next proof point, next commitments

## 3) Pages and UI

### 3.1 Portfolio Dashboard (home)

A table/grid of all VBUs/Products with at-a-glance fields:

Required columns:

- VBU/Product
- Lifecycle lane (Build/Sell/Milk/Reframe)
- 12--24m "success means..." sentence
- "Currently testing" (next review focus)
- Next review date (or "this month")
- Top 1 constraint/risk
- Proof-point health (simple indicator: On track / At risk / Stalled)

Interactions:

- Filter by lifecycle lane, GM, status (At risk/Stalled)
- Click through to VBU page
- Optional: "Portfolio notes" panel (free text) for you

### 3.2 VBU Page (detail)

Single page with sections matching the Canvas:

1.  Context + lifecycle lane selector
2.  Future State Intent
3.  Theses (editable list)
4.  Lifecycle implications (guardrails)
5.  Proof points (grouped by thesis; add evidence notes/links)
6.  Primary constraint/risk
7.  "Next monthly review" commitments + "currently testing" selector
8.  Monthly review history (chronological cards)

Important UX behaviour:

- Editing should be frictionless (inline edit, autosave or explicit
  Save).

- "Currently testing" should be a dropdown that points at:

  - a thesis, or
  - a specific proof point.

### 3.3 Monthly Review view (optional separate route)

A guided "wizard" that walks the GM through the four prompts and saves a
dated review entry.\
On completion, it asks for:

- next 1--3 commitments
- which thesis/proof point is now "primarily being tested"

## 4) Data model (minimum viable)

**Entities**

- *User* (name, email, role)
- *VBU* (name, GM owner)
- *Product* (name, belongs to VBU) or treat as one combined object if
  you prefer
- *Canvas* (1 per Product/VBU)
- *Thesis* (belongs to Canvas; order 1..5)
- *ProofPoint* (belongs to Thesis; status, evidence_notes, target_month)
- *MonthlyReview* (belongs to Canvas; date, answers to 4 prompts;
  commitments; "currently_testing" pointer)
- *AttachmentLink* (optional; URL + label, belongs to proof point or
  review)

**Roles**

- Admin (you): can view/edit all
- GM: can view/edit their VBU(s)
- Viewer: read-only

## 5) Non-functional requirements (keep it light)

- Auth: SSO if easy, otherwise email/password for pilot.
- Audit trail (minimal): updated_at + updated_by on Canvas and Review
  entries.
- Export: "Export Canvas to PDF" (optional nice-to-have) and/or "Copy to
  clipboard" text summary.

## 6) Implementation notes (to guide the AI dev)

- Start with a simple CRUD app: one relational DB (Postgres or SQLite
  for pilot), API endpoints, and a small React UI.
- Keep the UI opinionated: **evidence-first**, and always visible
  "currently testing" + "next commitments".
- Treat the Canvas as the "source of truth" and Monthly Reviews as the
  time-series learning log.
