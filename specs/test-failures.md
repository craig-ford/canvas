# Test Failures

## Summary
19 failed, 256 passed, 26 warnings in 96.03s

## Root Cause Groups

### Group A: Portfolio func.INTERVAL ORM bug (4 tests)
- FAILED tests/test_portfolio_routes.py::test_get_portfolio_summary_admin_sees_all
- FAILED tests/test_portfolio_routes.py::test_get_portfolio_summary_gm_sees_own_only
- FAILED tests/test_portfolio_routes.py::test_get_portfolio_summary_with_lane_filter
- FAILED tests/test_portfolio_routes.py::test_get_portfolio_summary_with_health_filter
Error: AttributeError: 'Comparator' object has no attribute '_is_tuple_type'
Cause: review-security agent rewrote raw SQL to ORM using invalid func.INTERVAL syntax

### Group B: Reviews 403 Forbidden (4 tests)
- FAILED tests/reviews/test_api_integration.py::TestReviewAPIIntegration::test_create_review_admin_any_canvas
- FAILED tests/reviews/test_api_integration.py::TestReviewAPIIntegration::test_create_review_gm_own_canvas_only
- FAILED tests/reviews/test_commitment_validation.py::TestCommitmentValidation::test_currently_testing_validation
- FAILED tests/reviews/test_commitment_validation.py::TestCommitmentValidation::test_duplicate_review_date_conflict
Error: Getting 403 Forbidden instead of expected status codes

### Group C: PDFService constructor changed (3 tests)
- FAILED tests/pdf/test_service.py::TestPDFServiceContract::test_service_instantiation
- FAILED tests/pdf/test_service.py::TestPDFServiceContract::test_export_canvas_signature
- FAILED tests/pdf/test_service.py::TestPDFServiceBehaviorContract::test_export_canvas_with_valid_uuid
Error: TypeError: PDFService.__init__() missing 1 required positional argument: 'db'

### Group D: Canvas/thesis validation changes (5 tests)
- FAILED tests/canvas/test_canvas_api.py::TestCanvasAPIValidation::test_update_canvas_empty_product_name (422 vs 500)
- FAILED tests/canvas/test_canvas_service_integration.py::TestCanvasServiceThesis::test_reorder_theses (IntegrityError)
- FAILED tests/canvas/test_thesis_api.py::TestThesisAPIValidation::test_create_thesis_duplicate_order (409 vs 201)
- FAILED tests/canvas/test_thesis_api.py::TestThesisAPIReordering::test_reorder_theses_success (422 vs 200)
- FAILED tests/canvas/test_thesis_api.py::TestThesisAPIReordering::test_reorder_theses_invalid_order (422 vs 200)

### Group E: Other (3 tests)
- FAILED tests/auth/test_auth_routes_integration.py::TestAuthRoutesIntegration::test_rate_limiting_login (429 vs 401)
- FAILED tests/canvas/test_proof_point_api.py::TestProofPointAPI::test_create_proof_point_validation_error (response shape)
- FAILED tests/canvas/test_vbu_api.py::TestVBUAPIValidation::test_create_vbu_invalid_gm_id (422 vs 500)
