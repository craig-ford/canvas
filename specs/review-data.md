# Canvas Data Handling Review Report

## Executive Summary

This review identified **23 data integrity and security issues** across the Canvas project, ranging from Critical to Low severity. Key concerns include missing foreign key constraints, polymorphic relationship validation gaps, SQL injection vulnerabilities, and inconsistent enum handling between models and migrations.

## Critical Issues

**SEVERITY: Critical**
**FILE: backend/canvas/models/attachment.py**
**LINE: 25**
**FEATURE: 002-canvas-management**
**TASK: T-003**
**ISSUE: Missing foreign key constraint for monthly_review_id**
**RATIONALE: Attachment model references monthly_reviews.id but migration 002_canvas_tables.py doesn't create this FK constraint, allowing orphaned attachments and data integrity violations**

**SEVERITY: Critical**
**FILE: backend/canvas/portfolio/service.py**
**LINE: 42**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-005**
**ISSUE: SQL injection vulnerability in dynamic query construction**
**RATIONALE: Raw SQL query with f-string interpolation of where_conditions allows potential SQL injection if filter values are not properly sanitized**

**SEVERITY: Critical**
**FILE: backend/canvas/models/canvas.py**
**LINE: 25**
**FEATURE: 002-canvas-management**
**TASK: T-003**
**ISSUE: Polymorphic currently_testing_id lacks referential integrity**
**RATIONALE: currently_testing_id can reference thesis.id or proof_point.id but no FK constraints enforce this, allowing dangling references and data corruption**

## High Severity Issues

**SEVERITY: High**
**FILE: backend/canvas/models/monthly_review.py**
**LINE: 15**
**FEATURE: 004-monthly-review**
**TASK: T-001**
**ISSUE: Enum definition mismatch between model and migration**
**RATIONALE: Model uses raw Enum() while migration creates testing_type enum, causing potential runtime failures and schema inconsistency**

**SEVERITY: High**
**FILE: backend/alembic/versions/002_canvas_tables.py**
**LINE: 145**
**FEATURE: 002-canvas-management**
**TASK: T-004**
**ISSUE: Missing foreign key constraint for monthly_review_id in attachments**
**RATIONALE: Migration creates attachment table but omits FK constraint to monthly_reviews, violating schema specification and allowing orphaned records**

**SEVERITY: High**
**FILE: backend/canvas/services/canvas_service.py**
**LINE: 85**
**FEATURE: 002-canvas-management**
**TASK: T-012**
**ISSUE: Missing validation for product_name empty string**
**RATIONALE: Service only checks .strip() but doesn't validate against empty string after strip, violating CHECK constraint and causing database errors**

**SEVERITY: High**
**FILE: backend/canvas/reviews/service.py**
**LINE: 45**
**FEATURE: 004-monthly-review**
**TASK: T-013**
**ISSUE: Missing polymorphic validation for currently_testing references**
**RATIONALE: _validate_currently_testing method is called but not implemented, allowing invalid thesis/proof_point references across canvases**

**SEVERITY: High**
**FILE: backend/canvas/db.py**
**LINE: 8**
**FEATURE: 001A-infrastructure**
**TASK: T-007**
**ISSUE: Missing connection pool configuration and error handling**
**RATIONALE: Database engine lacks pool settings, connection timeouts, and retry logic, risking connection exhaustion and poor error recovery**

## Medium Severity Issues

**SEVERITY: Medium**
**FILE: backend/canvas/models/user.py**
**LINE: 24**
**FEATURE: 001-auth**
**TASK: T-011**
**ISSUE: Redundant default value setting in __init__ method**
**RATIONALE: Model sets defaults in both Column definition and __init__, creating potential inconsistency and unnecessary complexity**

**SEVERITY: Medium**
**FILE: backend/canvas/models/commitment.py**
**LINE: 15**
**FEATURE: 004-monthly-review**
**TASK: T-002**
**ISSUE: Inconsistent constraint naming between model and migration**
**RATIONALE: Model uses length(text) while migration uses different constraint syntax, risking schema drift and maintenance issues**

**SEVERITY: Medium**
**FILE: backend/canvas/services/attachment_service.py**
**LINE: 18**
**FEATURE: 002-canvas-management**
**TASK: T-013**
**ISSUE: Hardcoded allowed file types don't match schema specification**
**RATIONALE: Service allows text/csv but schema constraint only permits specific Office/image formats, causing validation mismatch**

**SEVERITY: Medium**
**FILE: backend/canvas/reviews/schemas.py**
**LINE: 12**
**FEATURE: 004-monthly-review**
**TASK: T-004**
**ISSUE: Missing validation for currently_testing_type enum values**
**RATIONALE: Schema uses string pattern instead of enum validation, allowing invalid values that would fail at database level**

**SEVERITY: Medium**
**FILE: backend/alembic/versions/006_health_indicator_cache.py**
**LINE: 25**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-004**
**ISSUE: Complex trigger logic without error handling**
**RATIONALE: Health indicator trigger performs complex queries without error handling, risking trigger failures and inconsistent cache state**

**SEVERITY: Medium**
**FILE: backend/canvas/portfolio/service.py**
**LINE: 75**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-005**
**ISSUE: HTML escaping insufficient for XSS prevention**
**RATIONALE: Only uses html.escape() without context-aware encoding, insufficient protection against sophisticated XSS attacks in rich text contexts**

**SEVERITY: Medium**
**FILE: backend/canvas/config.py**
**LINE: 8**
**FEATURE: 001A-infrastructure**
**TASK: T-006**
**ISSUE: Missing validation for database_url format**
**RATIONALE: No validation that database_url is properly formatted PostgreSQL connection string, risking runtime connection failures**

## Low Severity Issues

**SEVERITY: Low**
**FILE: backend/canvas/models/__init__.py**
**LINE: 8**
**FEATURE: 001A-infrastructure**
**TASK: T-006**
**ISSUE: TimestampMixin lacks timezone validation**
**RATIONALE: DateTime columns specify timezone=True but no validation ensures timezone-aware datetime objects, risking naive datetime storage**

**SEVERITY: Low**
**FILE: backend/canvas/auth/service.py**
**LINE: 15**
**FEATURE: 001-auth**
**TASK: T-013**
**ISSUE: Hardcoded bcrypt rounds may be insufficient for future security**
**RATIONALE: bcrypt__rounds=12 is adequate now but should be configurable for future security requirements and performance tuning**

**SEVERITY: Low**
**FILE: backend/canvas/schemas.py**
**LINE: 45**
**FEATURE: 002-canvas-management**
**TASK: T-004**
**ISSUE: Missing field length validation for text fields**
**RATIONALE: Pydantic schemas don't enforce max_length on Text fields, allowing potentially oversized data that could impact performance**

**SEVERITY: Low**
**FILE: backend/canvas/models/thesis.py**
**LINE: 18**
**FEATURE: 002-canvas-management**
**TASK: T-003**
**ISSUE: Missing index on updated_at for audit queries**
**RATIONALE: No index on updated_at timestamp, impacting performance of audit trail queries and temporal data analysis**

**SEVERITY: Low**
**FILE: backend/canvas/models/proof_point.py**
**LINE: 20**
**FEATURE: 002-canvas-management**
**TASK: T-003**
**ISSUE: target_review_month lacks future date validation**
**RATIONALE: No constraint preventing target dates in the past, allowing logically invalid scheduling data**

**SEVERITY: Low**
**FILE: backend/canvas/seed.py**
**LINE: 10**
**FEATURE: 001A-infrastructure**
**TASK: T-012**
**ISSUE: Seed script is non-functional placeholder**
**RATIONALE: Seed script contains only blocked placeholders, preventing development environment setup and testing with realistic data**

**SEVERITY: Low**
**FILE: backend/alembic/versions/005_canvas_trigger.py**
**LINE: 18**
**FEATURE: 004-monthly-review**
**TASK: T-006**
**ISSUE: Trigger updates canvas without concurrency protection**
**RATIONALE: Canvas update trigger lacks row-level locking, risking race conditions in concurrent review creation scenarios**

**SEVERITY: Low**
**FILE: backend/canvas/reviews/service.py**
**LINE: 85**
**FEATURE: 004-monthly-review**
**TASK: T-013**
**ISSUE: Missing transaction rollback on attachment linking failure**
**RATIONALE: _link_attachments method not implemented but called, would cause transaction to hang without proper error handling**

**SEVERITY: Low**
**FILE: backend/canvas/services/canvas_service.py**
**LINE: 25**
**FEATURE: 002-canvas-management**
**TASK: T-012**
**ISSUE: VBU creation lacks duplicate name validation**
**RATIONALE: No uniqueness constraint on VBU names within same GM scope, allowing confusing duplicate VBU names**

## Data Migration Safety Issues

1. **Migration 002**: Missing FK constraint for attachments.monthly_review_id creates schema inconsistency
2. **Migration 004**: Enum type mismatch between model and migration definitions
3. **Migration 006**: Complex trigger without error handling risks database corruption
4. **Migration 005**: Canvas update trigger lacks concurrency protection

## Recommendations

### Immediate Actions (Critical/High)
1. Add missing FK constraints in new migration
2. Fix SQL injection vulnerability in portfolio service
3. Implement polymorphic reference validation
4. Standardize enum definitions across models and migrations
5. Add database connection pool configuration

### Medium Priority
1. Implement comprehensive input validation
2. Add proper error handling to database triggers
3. Standardize constraint naming conventions
4. Add missing indexes for performance

### Long Term
1. Implement comprehensive audit logging
2. Add data versioning for sensitive changes
3. Create automated data integrity checks
4. Establish database backup and recovery procedures

## Summary Statistics
- **Total Issues**: 23
- **Critical**: 3
- **High**: 5  
- **Medium**: 7
- **Low**: 8
- **Files Affected**: 15
- **Features Impacted**: All (001A-infrastructure, 001-auth, 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review)