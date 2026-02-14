# specs/schema.md

## Overview

Canvas uses a straightforward relational model centred on the VBU → Canvas 1:1 relationship. Each canvas contains ordered theses, each thesis has proof points. Monthly reviews capture dated evidence snapshots with commitments. Attachments are polymorphic (belong to either a proof point or a review). All entities use UUID primary keys and timestamp tracking.

## Entities

### User
**Feature:** 001-auth
**Table:** users

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login identifier |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash |
| name | VARCHAR(255) | NOT NULL | Display name |
| role | ENUM('admin','gm','viewer') | NOT NULL, default 'viewer' | Access level |
| is_active | BOOLEAN | NOT NULL, default True | Account active flag |
| last_login_at | TIMESTAMPTZ | NULLABLE | Last successful login |
| failed_login_attempts | INTEGER | NOT NULL, default 0 | Consecutive failed logins |
| locked_until | TIMESTAMPTZ | NULLABLE | Account lock expiry |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), on update now() | Last update |

**Indexes:**
- `ix_users_email` UNIQUE on email — login lookup
- `ix_users_role` on role — admin user listing

---

### VBU
**Feature:** 002-canvas-management
**Table:** vbus

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| name | VARCHAR(255) | NOT NULL, CHECK(LENGTH(TRIM(name)) > 0) | VBU display name |
| gm_id | UUID | FK → users.id ON DELETE RESTRICT, NOT NULL | Owning GM |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), on update now() | Last update |
| updated_by | UUID | FK → users.id ON DELETE SET NULL, NULLABLE | Last editor |

**Relationships:**
- belongs_to: User via gm_id
- has_one: Canvas

**Indexes:**
- `ix_vbus_gm_id` on gm_id — GM's VBU listing

---

### Canvas
**Feature:** 002-canvas-management
**Table:** canvases

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| vbu_id | UUID | FK → vbus.id ON DELETE CASCADE, UNIQUE, NOT NULL | 1:1 with VBU |
| product_name | VARCHAR(255) | NULLABLE, CHECK(product_name IS NULL OR LENGTH(TRIM(product_name)) > 0) | Optional product name |
| lifecycle_lane | ENUM('build','sell','milk','reframe') | NOT NULL, default 'build' | Current lane |
| success_description | TEXT | NULLABLE | "In this lane, success over 12-24 months means..." |
| future_state_intent | TEXT | NULLABLE | 3-5 year vision statement |
| primary_focus | VARCHAR(255) | NULLABLE | Learning / Replication / Cash & Risk |
| resist_doing | TEXT | NULLABLE | "What we must resist doing" |
| good_discipline | TEXT | NULLABLE | "What good discipline looks like" |
| primary_constraint | TEXT | NULLABLE | Single biggest blocker |
| currently_testing_type | ENUM('thesis','proof_point') | NULLABLE | Polymorphic type discriminator |
| currently_testing_id | UUID | NULLABLE | Polymorphic FK (thesis or proof_point) |
| portfolio_notes | TEXT | NULLABLE | Admin-only free text |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), on update now() | Last update |
| updated_by | UUID | FK → users.id ON DELETE SET NULL, NULLABLE | Last editor |

**Relationships:**
- belongs_to: VBU via vbu_id (1:1)
- has_many: Thesis (max 5, ordered)
- has_many: MonthlyReview

**Indexes:**
- `ix_canvases_vbu_id` UNIQUE on vbu_id — 1:1 enforcement + lookup

---

### Thesis
**Feature:** 002-canvas-management
**Table:** theses

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| canvas_id | UUID | FK → canvases.id ON DELETE CASCADE, NOT NULL | Parent canvas |
| order | INTEGER | NOT NULL, CHECK(order BETWEEN 1 AND 5) | Display order |
| text | TEXT | NOT NULL, CHECK(LENGTH(TRIM(text)) > 0) | Thesis statement |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), on update now() | Last update |

**Relationships:**
- belongs_to: Canvas via canvas_id
- has_many: ProofPoint

**Indexes:**
- `ix_theses_canvas_id` on canvas_id — canvas's theses listing
- `uq_theses_canvas_order` UNIQUE on (canvas_id, order) — no duplicate ordering

---

### ProofPoint
**Feature:** 002-canvas-management
**Table:** proof_points

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| thesis_id | UUID | FK → theses.id ON DELETE CASCADE, NOT NULL | Parent thesis |
| description | TEXT | NOT NULL, CHECK(LENGTH(TRIM(description)) > 0) | Observable signal description |
| status | ENUM('not_started','in_progress','observed','stalled') | NOT NULL, default 'not_started' | Current status |
| evidence_note | TEXT | NULLABLE | Evidence supporting status |
| target_review_month | DATE | NULLABLE | Target month for observation |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, server default now(), on update now() | Last update |

**Relationships:**
- belongs_to: Thesis via thesis_id
- has_many: Attachment

**Indexes:**
- `ix_proof_points_thesis_id` on thesis_id — thesis's proof points listing
- `ix_proof_points_status` on status — dashboard health aggregation

---

### MonthlyReview
**Feature:** 004-monthly-review
**Table:** monthly_reviews

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| canvas_id | UUID | FK → canvases.id ON DELETE CASCADE, NOT NULL | Parent canvas |
| review_date | DATE | NOT NULL | Review date |
| what_moved | TEXT | NULLABLE | "What moved since last month (evidence)?" |
| what_learned | TEXT | NULLABLE | "What did we learn that changes our beliefs?" |
| what_threatens | TEXT | NULLABLE | "What now threatens the next proof point?" |
| currently_testing_type | ENUM('thesis','proof_point') | NULLABLE | What was selected as focus |
| currently_testing_id | UUID | NULLABLE | Polymorphic FK |
| created_by | UUID | FK → users.id ON DELETE RESTRICT, NOT NULL | Review author |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |

**Relationships:**
- belongs_to: Canvas via canvas_id
- has_many: Commitment (max 3, ordered)
- has_many: Attachment

**Indexes:**
- `ix_monthly_reviews_canvas_id` on canvas_id — canvas's review listing
- `ix_monthly_reviews_review_date` on review_date — chronological ordering

---

### Commitment
**Feature:** 004-monthly-review
**Table:** commitments

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| monthly_review_id | UUID | FK → monthly_reviews.id ON DELETE CASCADE, NOT NULL | Parent review |
| text | TEXT | NOT NULL, CHECK(length(text) BETWEEN 1 AND 1000) | Commitment text |
| order | INTEGER | NOT NULL, CHECK(order BETWEEN 1 AND 3) | Display order |

**Relationships:**
- belongs_to: MonthlyReview via monthly_review_id

**Indexes:**
- `ix_commitments_review_id` on monthly_review_id — review's commitments listing

---

### Attachment
**Feature:** 002-canvas-management
**Table:** attachments

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| proof_point_id | UUID | FK → proof_points.id ON DELETE CASCADE, NULLABLE | Attached to proof point |
| monthly_review_id | UUID | FK → monthly_reviews.id ON DELETE CASCADE, NULLABLE | Attached to review |
| filename | VARCHAR(255) | NOT NULL, CHECK(LENGTH(TRIM(filename)) > 0) | Original filename |
| storage_path | VARCHAR(1024) | UNIQUE, NOT NULL, CHECK(LENGTH(TRIM(storage_path)) > 0) | Path on disk |
| content_type | VARCHAR(128) | NOT NULL, CHECK(content_type IN ('image/jpeg','image/png','image/gif','application/pdf','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.presentationml.presentation')) | MIME type |
| size_bytes | INTEGER | NOT NULL, CHECK(size_bytes BETWEEN 1 AND 10485760) | File size (max 10MB) |
| label | VARCHAR(255) | NULLABLE, CHECK(label IS NULL OR LENGTH(TRIM(label)) > 0) | User-provided label |
| uploaded_by | UUID | FK → users.id ON DELETE RESTRICT, NOT NULL | Uploader |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Upload timestamp |

**Relationships:**
- belongs_to: ProofPoint via proof_point_id (nullable)
- belongs_to: MonthlyReview via monthly_review_id (nullable)

**Constraints:**
- CHECK: exactly one of (proof_point_id, monthly_review_id) is NOT NULL

**Indexes:**
- `ix_attachments_proof_point_id` on proof_point_id — proof point's attachments
- `ix_attachments_monthly_review_id` on monthly_review_id — review's attachments

---

## Relationship Diagram

```
[User] 1──────* [VBU]
                  │
                  1
                  │
               [Canvas] 1──────* [Thesis] 1──────* [ProofPoint]
                  │                                      │
                  1                                      *
                  │                                      │
                  *                               [Attachment]
                  │                                      │
           [MonthlyReview] 1──────* [Commitment]         *
                  │                                      │
                  *──────────────────────────────[Attachment]
```

## Changelog

| Date | Feature | Change |
|------|---------|--------|
| 2026-02-13 | bootstrap | Initial schema from application.md |
