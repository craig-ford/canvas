# Test Failures — Attempt 2 (Post-Subagent Round 1)

## Summary
40 failed, 222 passed, 23 warnings in 66.85s

## Progress
- Attempt 1: 127 passed, 50 failed, 89 errors (266 total)
- Attempt 2 start: 193 passed, 59 failed, 10 errors (after previous session fixes)
- After shared root cause fixes: 212 passed, 50 failed, 0 errors
- After subagent round 1: 222 passed, 40 failed, 0 errors

## Remaining Failures by File (40)

### tests/canvas/test_proof_point_api.py (8 failures)
- test_get_proof_points_success, test_get_proof_points_unauthorized, test_create_proof_point_forbidden_viewer
- test_update_proof_point_success, test_update_proof_point_status_change, test_update_proof_point_forbidden_other_gm
- test_delete_proof_point_success, test_delete_proof_point_not_found
- Subagent 1 rewrote to use conftest fixtures but tests still fail — likely wrong API paths or response shapes

### tests/test_pdf_routes.py (5 failures)
- All 5 PDF export tests still return 500
- PDF template path was fixed (backend/ prefix removed) but still failing — may need to check if template renders correctly or if there's another issue

### tests/reviews/test_api_integration.py (4 failures)
- test_list_reviews_gm_access_own_canvas_only, test_create_review_admin_any_canvas
- test_create_review_gm_own_canvas_only, test_get_review_authorization_matrix
- Subagent 2 fixed endpoints and fixtures but tests still fail

### tests/reviews/test_service_integration.py (4 failures)
- test_create_review_with_commitments, test_create_review_updates_canvas_currently_testing
- test_attachment_linking_integration, test_validate_currently_testing_belongs_to_canvas

### tests/canvas/test_canvas_api.py (4 failures)
- test_update_canvas_gm_own, test_update_canvas_empty_product_name
- test_update_portfolio_notes_admin, test_update_portfolio_notes_gm_ignored

### tests/canvas/test_attachment_service_integration.py (4 failures)
- test_upload_valid_file, test_download_existing_file, test_delete_existing_file, test_storage_path_generation

### tests/canvas/test_attachment_api.py (3 failures)
- test_download_file_not_found, test_upload_nonexistent_proof_point, test_delete_not_found

### tests/canvas/test_thesis_api.py (3 failures)
- test_create_thesis_duplicate_order, test_reorder_theses_success, test_reorder_theses_invalid_order

### tests/canvas/test_vbu_api.py (2 failures)
- test_update_vbu_gm_own, test_create_vbu_invalid_gm_id

### tests/reviews/test_commitment_validation.py (2 failures)
- test_currently_testing_validation, test_duplicate_review_date_conflict

### tests/canvas/test_canvas_service_integration.py (1 failure)
- test_reorder_theses
