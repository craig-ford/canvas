# Backend Code Review Report

## Runtime Errors Found

**SEVERITY: Critical**
**FILE: Database Logs**
**LINE: N/A**
**FEATURE: Multiple**
**TASK: Multiple**
**ISSUE: Multiple database constraint violations in production**
**RATIONALE: Active constraint violations indicate data integrity issues and potential application bugs**

Database errors found:
- Duplicate key violations on `ix_users_email` (user registration conflicts)
- Check constraint violations on `ck_thesis_order_range` (invalid thesis ordering)
- Duplicate key violations on `uq_monthly_reviews_canvas_date` (duplicate review dates)
- Null constraint violations on commitments.text (missing validation)

## Static Code Issues

### Critical Issues

**SEVERITY: Critical**
**FILE: backend/canvas/auth/service.py**
**LINE: 95**
**FEATURE: 001-auth**
**TASK: T-013**
**ISSUE: Syntax error in is_account_locked method - missing return statement**
**RATIONALE: Method ends with incomplete comparison, will cause runtime AttributeError**

**SEVERITY: Critical**
**FILE: backend/canvas/auth/schemas.py**
**LINE: 14**
**FEATURE: 001-auth**
**TASK: T-016**
**ISSUE: Deprecated Pydantic v1 Config class usage**
**RATIONALE: Using deprecated `class Config` instead of `model_config = ConfigDict()` causes deprecation warnings**

**SEVERITY: Critical**
**FILE: backend/canvas/portfolio/router.py**
**LINE: 59**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-007**
**ISSUE: Deprecated Pydantic .dict() method usage**
**RATIONALE: Using deprecated `.dict()` instead of `.model_dump()` causes deprecation warnings**

### High Issues

**SEVERITY: High**
**FILE: backend/canvas/main.py**
**LINE: 30-35**
**FEATURE: 001A-infrastructure**
**TASK: T-008**
**ISSUE: Redundant CORS middleware configuration**
**RATIONALE: Both CORSMiddleware and custom middleware add CORS headers, potential for conflicts**

**SEVERITY: High**
**FILE: backend/canvas/services/canvas_service.py**
**LINE: 175-185**
**FEATURE: 002-canvas-management**
**TASK: T-012**
**ISSUE: Unsafe constraint manipulation in reorder_theses**
**RATIONALE: Dropping and recreating constraints during transaction can cause data integrity issues**

**SEVERITY: High**
**FILE: backend/canvas/routes/attachment.py**
**LINE: 45-65**
**FEATURE: 002-canvas-management**
**TASK: T-018**
**ISSUE: Complex nested authorization logic with N+1 query potential**
**RATIONALE: Multiple database queries for authorization check, inefficient and hard to maintain**

**SEVERITY: High**
**FILE: backend/canvas/portfolio/service.py**
**LINE: 25-45**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-005**
**ISSUE: Raw SQL query with potential injection risk**
**RATIONALE: Using f-string formatting in SQL query construction, should use parameterized queries**

**SEVERITY: High**
**FILE: backend/canvas/reviews/service.py**
**LINE: 45-55**
**FEATURE: 004-monthly-review**
**TASK: T-013**
**ISSUE: Missing transaction rollback on validation failure**
**RATIONALE: Database operations not properly wrapped in try/catch with rollback**

### Medium Issues

**SEVERITY: Medium**
**FILE: backend/canvas/config.py**
**LINE: 1-15**
**FEATURE: 001A-infrastructure**
**TASK: T-006**
**ISSUE: Missing validation for required environment variables**
**RATIONALE: No validation that critical config values like database_url and secret_key are provided**

**SEVERITY: Medium**
**FILE: backend/canvas/db.py**
**LINE: 8-10**
**FEATURE: 001A-infrastructure**
**TASK: T-007**
**ISSUE: Global settings instance created at module level**
**RATIONALE: Settings should be dependency-injected for better testability and configuration management**

**SEVERITY: Medium**
**FILE: backend/canvas/auth/dependencies.py**
**LINE: 35-45**
**FEATURE: 001-auth**
**TASK: T-015**
**ISSUE: Inconsistent role validation logic**
**RATIONALE: Complex role normalization that accepts both enums and strings, potential for confusion**

**SEVERITY: Medium**
**FILE: backend/canvas/models/user.py**
**LINE: 15-25**
**FEATURE: 001-auth**
**TASK: T-011**
**ISSUE: Redundant default value setting in __init__**
**RATIONALE: Setting defaults in both column definition and __init__ method is unnecessary**

**SEVERITY: Medium**
**FILE: backend/canvas/routes/thesis.py**
**LINE: 65-75**
**FEATURE: 002-canvas-management**
**TASK: T-016**
**ISSUE: Inconsistent error handling for IntegrityError**
**RATIONALE: Generic exception handling that doesn't properly distinguish between different constraint violations**

**SEVERITY: Medium**
**FILE: backend/canvas/services/attachment_service.py**
**LINE: 35-45**
**FEATURE: 002-canvas-management**
**TASK: T-013**
**ISSUE: Hardcoded allowed file types**
**RATIONALE: File type restrictions should be configurable, not hardcoded in service**

**SEVERITY: Medium**
**FILE: backend/canvas/pdf/service.py**
**LINE: 35-40**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-006**
**ISSUE: Hardcoded template path**
**RATIONALE: Template path should be configurable, not hardcoded string**

**SEVERITY: Medium**
**FILE: backend/alembic/versions/002_canvas_tables.py**
**LINE: 15-20**
**FEATURE: 002-canvas-management**
**TASK: T-004**
**ISSUE: Inconsistent revision naming**
**RATIONALE: Revision references '001_auth_tables' but actual file is '001_create_users_table.py'**

### Low Issues

**SEVERITY: Low**
**FILE: backend/canvas/__init__.py**
**LINE: 5-15**
**FEATURE: 001A-infrastructure**
**TASK: T-006**
**ISSUE: Missing type hints on response helper functions**
**RATIONALE: Functions lack proper type annotations for better IDE support and documentation**

**SEVERITY: Low**
**FILE: backend/canvas/seed.py**
**LINE: 10-30**
**FEATURE: 001A-infrastructure**
**TASK: T-012**
**ISSUE: Placeholder implementation with blocking comments**
**RATIONALE: Seed script is not functional, contains only placeholder code**

**SEVERITY: Low**
**FILE: backend/canvas/models/__init__.py**
**LINE: 25-35**
**FEATURE: 001A-infrastructure**
**TASK: T-006**
**ISSUE: Circular import potential with model exports**
**RATIONALE: Importing all models in __init__.py can cause circular import issues**

**SEVERITY: Low**
**FILE: backend/canvas/routes/proof_point.py**
**LINE: 25-30**
**FEATURE: 002-canvas-management**
**TASK: T-017**
**ISSUE: Inconsistent date format validation**
**RATIONALE: Using regex pattern for date validation instead of proper date parsing**

**SEVERITY: Low**
**FILE: backend/canvas/portfolio/schemas.py**
**LINE: 5-10**
**FEATURE: 003-portfolio-dashboard**
**TASK: T-001**
**ISSUE: Duplicate LifecycleLane enum definition**
**RATIONALE: LifecycleLane enum already defined in canvas.models.canvas, should import instead**

**SEVERITY: Low**
**FILE: backend/canvas/reviews/schemas.py**
**LINE: 45-50**
**FEATURE: 004-monthly-review**
**TASK: T-014**
**ISSUE: Missing field validation on ReviewResponse**
**RATIONALE: Response schema lacks validation for optional fields that could be empty strings**

## Code Hygiene Issues

### Orphan Files
- `backend/canvas/vbus/` directory exists but is empty
- `backend/canvas/pdf/test_service.py` appears to be a test file in wrong location

### God Files
- `backend/canvas/services/canvas_service.py` (14KB, 400+ lines) - handles too many responsibilities
- `backend/canvas/routes/attachment.py` (7KB, 200+ lines) - complex authorization logic mixed with file handling

### Missing Error Handling
- No global exception handler for database connection failures
- Missing validation for file upload edge cases (empty files, corrupted uploads)
- No rate limiting on authentication endpoints
- Missing request size limits on file uploads

### Security Issues
- JWT tokens don't include issued-at (iat) claim for better security
- No CSRF protection on state-changing endpoints
- File upload paths not properly sanitized
- Portfolio notes HTML escaping only in service layer, not at input validation

### Performance Issues
- N+1 queries in attachment authorization checks
- Missing database connection pooling configuration
- No caching for frequently accessed data (user roles, VBU ownership)
- Raw SQL queries without proper query optimization

## Recommendations

1. **Fix Critical Issues First**: Address syntax errors and deprecated API usage
2. **Implement Proper Error Handling**: Add comprehensive try/catch blocks with proper rollback
3. **Refactor Large Services**: Break down CanvasService into smaller, focused services
4. **Add Input Validation**: Implement proper validation at API boundary
5. **Optimize Database Access**: Use proper eager loading and reduce N+1 queries
6. **Improve Security**: Add rate limiting, CSRF protection, and better token validation
7. **Add Monitoring**: Implement structured logging and error tracking
8. **Complete Placeholder Code**: Finish seed script and other incomplete implementations

## Summary

- **Critical Issues**: 3 (syntax errors, deprecated APIs)
- **High Issues**: 5 (security, performance, data integrity)
- **Medium Issues**: 8 (maintainability, configuration)
- **Low Issues**: 6 (code quality, consistency)

The codebase shows good architectural structure but has several critical issues that need immediate attention, particularly around error handling, deprecated API usage, and database integrity.