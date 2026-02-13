#!/usr/bin/env python3

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Build file-to-feature mapping from file-map.md
def build_file_map() -> Dict[str, Tuple[str, str]]:
    """Returns dict mapping file path to (feature, task)"""
    file_map = {}
    
    file_map_content = """
| backend/canvas/models/user.py | 001-auth | T-001 | CREATE |
| backend/tests/models/test_user_contract.py | 001-auth | T-001 | CREATE |
| backend/canvas/auth/service.py | 001-auth | T-002 | CREATE |
| backend/tests/auth/test_auth_service_contract.py | 001-auth | T-002 | CREATE |
| backend/canvas/auth/user_service.py | 001-auth | T-003 | CREATE |
| backend/canvas/auth/dependencies.py | 001-auth | T-004 | CREATE |
| backend/tests/auth/test_auth_dependencies_contract.py | 001-auth | T-004 | CREATE |
| backend/tests/auth/test_auth_routes_integration.py | 001-auth | T-005 | CREATE |
| backend/tests/auth/test_user_routes.py | 001-auth | T-006 | CREATE |
| tests/test_rate_limiting_integration.py | 001-auth | T-007 | CREATE |
| backend/tests/test_user_model.py | 001-auth | T-008 | CREATE |
| tests/test_auth_service_unit.py | 001-auth | T-009 | CREATE |
| backend/tests/auth/test_user_service.py | 001-auth | T-010 | CREATE |
| backend/canvas/models/user.py | 001-auth | T-011 | MODIFY |
| backend/alembic/versions/001_create_users_table.py | 001-auth | T-012 | CREATE |
| backend/canvas/auth/service.py | 001-auth | T-013 | MODIFY |
| backend/canvas/auth/user_service.py | 001-auth | T-014 | MODIFY |
| backend/canvas/auth/dependencies.py | 001-auth | T-015 | CREATE |
| backend/canvas/auth/routes.py | 001-auth | T-016 | CREATE |
| backend/tests/test_models_contract.py | 001A-infrastructure | T-001 | CREATE |
| backend/tests/test_responses_contract.py | 001A-infrastructure | T-001 | CREATE |
| backend/tests/test_config_contract.py | 001A-infrastructure | T-002 | CREATE |
| backend/tests/test_db_contract.py | 001A-infrastructure | T-003 | CREATE |
| backend/tests/test_health_contract.py | 001A-infrastructure | T-004 | CREATE |
| backend/tests/test_docker_integration.py | 001A-infrastructure | T-005 | CREATE |
| backend/canvas/models/__init__.py | 001A-infrastructure | T-006 | CREATE |
| backend/canvas/config.py | 001A-infrastructure | T-006 | CREATE |
| backend/canvas/__init__.py | 001A-infrastructure | T-006 | CREATE |
| backend/canvas/db.py | 001A-infrastructure | T-007 | CREATE |
| backend/alembic.ini | 001A-infrastructure | T-007 | CREATE |
| backend/canvas/main.py | 001A-infrastructure | T-008 | CREATE |
| backend/canvas/main.py | 001A-infrastructure | T-009 | MODIFY |
| docker-compose.yml | 001A-infrastructure | T-010 | CREATE |
| backend/Dockerfile | 001A-infrastructure | T-010 | CREATE |
| frontend/Dockerfile | 001A-infrastructure | T-010 | CREATE |
| frontend/src/api/client.ts | 001A-infrastructure | T-011 | CREATE |
| frontend/src/components/AppShell.tsx | 001A-infrastructure | T-011 | CREATE |
| backend/canvas/seed.py | 001A-infrastructure | T-012 | CREATE |
| backend/canvas/services/canvas_service.py | 002-canvas-management | T-001 | CREATE |
| tests/canvas/test_canvas_service_contract.py | 002-canvas-management | T-001 | CREATE |
| backend/canvas/services/attachment_service.py | 002-canvas-management | T-002 | CREATE |
| tests/canvas/test_attachment_service_contract.py | 002-canvas-management | T-002 | CREATE |
| backend/canvas/models/vbu.py | 002-canvas-management | T-003 | CREATE |
| backend/canvas/models/canvas.py | 002-canvas-management | T-003 | CREATE |
| backend/canvas/models/thesis.py | 002-canvas-management | T-003 | CREATE |
| backend/canvas/models/proof_point.py | 002-canvas-management | T-003 | CREATE |
| backend/canvas/models/attachment.py | 002-canvas-management | T-003 | CREATE |
| backend/canvas/models/__init__.py | 002-canvas-management | T-003 | MODIFY |
| backend/canvas/schemas.py | 002-canvas-management | T-004 | CREATE |
| backend/tests/test_canvas_models.py | 002-canvas-management | T-005 | CREATE |
| backend/tests/test_canvas_authorization.py | 002-canvas-management | T-006 | CREATE |
| backend/tests/test_vbu_service.py | 002-canvas-management | T-007 | CREATE |
| backend/tests/test_canvas_service.py | 002-canvas-management | T-008 | CREATE |
| backend/tests/test_thesis_service.py | 002-canvas-management | T-009 | CREATE |
| backend/tests/test_proof_point_service.py | 002-canvas-management | T-010 | CREATE |
| backend/tests/unit/test_attachment_service.py | 002-canvas-management | T-011 | CREATE |
| backend/canvas/services/canvas_service.py | 002-canvas-management | T-012 | MODIFY |
| backend/canvas/services/attachment_service.py | 002-canvas-management | T-013 | CREATE |
| backend/canvas/routes/vbu.py | 002-canvas-management | T-014 | CREATE |
| backend/canvas/routes/canvas.py | 002-canvas-management | T-015 | CREATE |
| backend/canvas/routes/thesis.py | 002-canvas-management | T-016 | CREATE |
| backend/canvas/routes/proof_point.py | 002-canvas-management | T-017 | CREATE |
| backend/canvas/routes/attachment.py | 002-canvas-management | T-018 | CREATE |
| backend/canvas/cli.py | 002-canvas-management | T-019 | CREATE |
| alembic/versions/002_canvas_tables.py | 002-canvas-management | T-020 | CREATE |
| backend/canvas/portfolio/schemas.py | 003-portfolio-dashboard | T-001 | CREATE |
| backend/canvas/portfolio/service.py | 003-portfolio-dashboard | T-001 | CREATE |
| tests/test_portfolio_service.py | 003-portfolio-dashboard | T-001 | CREATE |
| backend/canvas/pdf/test_service.py | 003-portfolio-dashboard | T-002 | CREATE |
| backend/canvas/portfolio/router.py | 003-portfolio-dashboard | T-003 | CREATE |
| tests/test_portfolio_api.py | 003-portfolio-dashboard | T-003 | CREATE |
| backend/canvas/models/canvas.py | 003-portfolio-dashboard | T-004 | MODIFY |
| alembic/versions/add_health_indicator_cache.py | 003-portfolio-dashboard | T-004 | CREATE |
| backend/canvas/portfolio/service.py | 003-portfolio-dashboard | T-005 | MODIFY |
| tests/test_portfolio_service_impl.py | 003-portfolio-dashboard | T-005 | CREATE |
| backend/canvas/pdf/service.py | 003-portfolio-dashboard | T-006 | CREATE |
| backend/canvas/pdf/templates/canvas.html | 003-portfolio-dashboard | T-006 | CREATE |
| backend/canvas/pdf/__init__.py | 003-portfolio-dashboard | T-006 | CREATE |
| backend/canvas/portfolio/router.py | 003-portfolio-dashboard | T-007 | MODIFY |
| tests/test_portfolio_routes.py | 003-portfolio-dashboard | T-007 | CREATE |
| backend/canvas/vbus/test_pdf_routes.py | 003-portfolio-dashboard | T-008 | CREATE |
| backend/canvas/vbus/router.py | 003-portfolio-dashboard | T-008 | MODIFY |
| frontend/src/dashboard/__tests__/DashboardPage.test.tsx | 003-portfolio-dashboard | T-009 | CREATE |
| frontend/src/dashboard/__tests__/VBUTable.test.tsx | 003-portfolio-dashboard | T-010 | CREATE |
| frontend/src/dashboard/__tests__/HealthIndicator.test.tsx | 003-portfolio-dashboard | T-011 | CREATE |
| frontend/src/dashboard/PortfolioNotes.test.tsx | 003-portfolio-dashboard | T-012 | CREATE |
| frontend/src/dashboard/HealthIndicator.test.tsx | 003-portfolio-dashboard | T-013 | CREATE |
| frontend/src/dashboard/DashboardPage.tsx | 003-portfolio-dashboard | T-014 | CREATE |
| frontend/src/dashboard/hooks/usePortfolio.ts | 003-portfolio-dashboard | T-014 | CREATE |
| frontend/src/dashboard/VBUTable.tsx | 003-portfolio-dashboard | T-015 | CREATE |
| frontend/src/dashboard/HealthIndicator.tsx | 003-portfolio-dashboard | T-016 | CREATE |
| frontend/src/dashboard/PortfolioNotes.tsx | 003-portfolio-dashboard | T-017 | CREATE |
| frontend/src/dashboard/HealthIndicator.tsx | 003-portfolio-dashboard | T-018 | MODIFY |
| backend/canvas/models/monthly_review.py | 004-monthly-review | T-001 | CREATE |
| backend/canvas/models/commitment.py | 004-monthly-review | T-002 | CREATE |
| backend/canvas/reviews/service.py | 004-monthly-review | T-003 | CREATE |
| backend/canvas/reviews/schemas.py | 004-monthly-review | T-004 | CREATE |
| alembic/versions/004_monthly_reviews.py | 004-monthly-review | T-005 | CREATE |
| alembic/versions/xxx_canvas_trigger.py | 004-monthly-review | T-006 | CREATE |
| backend/tests/reviews/test_service_integration.py | 004-monthly-review | T-007 | CREATE |
| backend/tests/reviews/test_api_integration.py | 004-monthly-review | T-008 | CREATE |
| backend/tests/reviews/test_commitment_validation.py | 004-monthly-review | T-009 | CREATE |
| backend/tests/reviews/test_service_unit.py | 004-monthly-review | T-010 | CREATE |
| backend/tests/models/test_monthly_review_relationships.py | 004-monthly-review | T-011 | CREATE |
| backend/tests/schemas/test_commitment_validation.py | 004-monthly-review | T-012 | CREATE |
| backend/canvas/reviews/service.py | 004-monthly-review | T-013 | CREATE |
| backend/canvas/reviews/router.py | 004-monthly-review | T-014 | CREATE |
| backend/canvas/reviews/schemas.py | 004-monthly-review | T-014 | CREATE |
| frontend/src/reviews/ReviewWizard.tsx | 004-monthly-review | T-015 | CREATE |
| frontend/src/reviews/components/StepIndicator.tsx | 004-monthly-review | T-015 | CREATE |
| frontend/src/reviews/components/WhatMovedStep.tsx | 004-monthly-review | T-015 | CREATE |
| frontend/src/reviews/components/CommitmentsStep.tsx | 004-monthly-review | T-015 | CREATE |
| frontend/src/reviews/ReviewHistory.tsx | 004-monthly-review | T-016 | CREATE |
| frontend/src/reviews/ReviewWizard.tsx | 004-monthly-review | T-017 | MODIFY |
| frontend/src/reviews/hooks/useAutoSave.ts | 004-monthly-review | T-017 | CREATE |
| frontend/src/reviews/components/FileUploadStep.tsx | 004-monthly-review | T-017 | CREATE |
| frontend/src/App.tsx | 004-monthly-review | T-018 | MODIFY |
| frontend/src/canvas/CanvasPage.tsx | 004-monthly-review | T-018 | MODIFY |
| frontend/src/reviews/index.ts | 004-monthly-review | T-018 | CREATE |
| frontend/src/App.tsx | 003-portfolio-dashboard | T-014 | MODIFY |
"""
    
    for line in file_map_content.strip().split('\n'):
        if '|' in line and not line.startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                file_path = parts[1]
                feature = parts[2]
                task = parts[3]
                if file_path and feature and task:
                    file_map[file_path] = (feature, task)
    
    return file_map

# Standard library and third-party imports to skip
SKIP_IMPORTS = {
    'datetime', 'uuid', 'typing', 'os', 'json', 're', 'pathlib', 'enum', 'abc', 
    'dataclasses', 'functools', 'itertools', 'collections', 'contextlib', 
    'logging', 'asyncio', 'decimal', 'Any', 'Optional', 'List', 'Dict', 'Union', 
    'Callable', 'TypeVar', 'Generic', 'Protocol', 'Literal', 'Tuple', 'Set',
    'pydantic', 'sqlalchemy', 'fastapi', 'pytest', 'httpx', 'aiohttp', 'celery', 
    'redis', 'numpy', 'pandas'
}

def extract_imports_from_contract(content: str) -> List[str]:
    """Extract Python imports from Contract section"""
    imports = []
    
    # Find Contract section
    contract_match = re.search(r'## Contract\s*```python(.*?)```', content, re.DOTALL)
    if not contract_match:
        return imports
    
    contract_code = contract_match.group(1)
    
    # Extract import statements - focus on canvas.* imports
    import_patterns = [
        r'from\s+(canvas[\w\.]*)\s+import',
        r'import\s+(canvas[\w\.]*)'
    ]
    
    for pattern in import_patterns:
        matches = re.findall(pattern, contract_code, re.MULTILINE)
        for match in matches:
            imports.append(match)
    
    return imports

def convert_import_to_file_path(import_module: str) -> str:
    """Convert Python import to file path"""
    # Handle relative imports like canvas.models.base -> backend/canvas/models/base.py
    if import_module.startswith('canvas.'):
        return f"backend/{import_module.replace('.', '/')}.py"
    elif import_module.startswith('frontend.'):
        return f"{import_module.replace('.', '/')}.py"
    else:
        return f"{import_module.replace('.', '/')}.py"

def should_skip_import(import_module: str) -> bool:
    """Check if import should be skipped (stdlib/third-party)"""
    module_parts = import_module.split('.')
    return any(part in SKIP_IMPORTS for part in module_parts)

def extract_predecessor_table(content: str) -> List[Dict[str, str]]:
    """Extract Cross-Feature predecessor table entries"""
    entries = []
    
    # Find Cross-Feature table
    cross_feature_match = re.search(
        r'### Cross-Feature\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|(.*?)(?=###|\n\n|\Z)', 
        content, re.DOTALL
    )
    
    if not cross_feature_match:
        return entries
    
    table_content = cross_feature_match.group(1)
    
    # Parse table rows
    for line in table_content.split('\n'):
        if '|' in line and not line.strip().startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                feature = parts[1]
                file_path = parts[2]
                task = parts[3]
                import_stmt = parts[4]
                
                if feature and file_path and task and import_stmt:
                    entries.append({
                        'feature': feature,
                        'file': file_path,
                        'task': task,
                        'import': import_stmt
                    })
    
    return entries

def analyze_task_file(file_path: str, file_map: Dict[str, Tuple[str, str]]) -> Dict:
    """Analyze a single task file for cross-feature imports"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except:
        return {'error': f'Could not read {file_path}'}
    
    # Extract feature and task from file path
    path_parts = file_path.split('/')
    if len(path_parts) < 4:
        return {'error': f'Invalid path format: {file_path}'}
    
    feature = path_parts[1]  # specs/FEATURE/tasks/T-*.md
    task = path_parts[3].replace('.md', '')  # T-001
    
    # Extract imports from Contract section
    contract_imports = extract_imports_from_contract(content)
    
    # Extract Cross-Feature predecessor table
    predecessor_entries = extract_predecessor_table(content)
    
    # Analyze cross-feature imports
    cross_feature_imports = []
    unresolvable_imports = []
    
    for import_module in contract_imports:
        if should_skip_import(import_module):
            continue
            
        file_path_from_import = convert_import_to_file_path(import_module)
        
        if file_path_from_import in file_map:
            source_feature, source_task = file_map[file_path_from_import]
            if source_feature != feature:  # Cross-feature
                cross_feature_imports.append({
                    'import': import_module,
                    'file': file_path_from_import,
                    'source_feature': source_feature,
                    'source_task': source_task
                })
        else:
            unresolvable_imports.append({
                'import': import_module,
                'file': file_path_from_import
            })
    
    # Check for missing predecessors and TBDs
    missing_predecessors = []
    unresolved_tbds = []
    
    for cross_import in cross_feature_imports:
        # Look for matching entry in predecessor table
        found = False
        for entry in predecessor_entries:
            if (entry['feature'] == cross_import['source_feature'] and 
                entry['file'] == cross_import['file']):
                found = True
                if entry['task'] == 'TBD':
                    unresolved_tbds.append({
                        'feature': feature,
                        'task': task,
                        'file': cross_import['file'],
                        'should_be': cross_import['source_task']
                    })
                break
        
        if not found:
            missing_predecessors.append({
                'feature': feature,
                'task': task,
                'import': cross_import['import'],
                'source_feature': cross_import['source_feature'],
                'source_task': cross_import['source_task']
            })
    
    return {
        'feature': feature,
        'task': task,
        'cross_feature_imports': cross_feature_imports,
        'unresolvable_imports': unresolvable_imports,
        'missing_predecessors': missing_predecessors,
        'unresolved_tbds': unresolved_tbds
    }

def main():
    file_map = build_file_map()
    
    # Find all task files
    task_files = []
    for root, dirs, files in os.walk('specs'):
        for file in files:
            if file.startswith('T-') and file.endswith('.md'):
                task_files.append(os.path.join(root, file))
    
    # Analyze all task files
    results = []
    for task_file in task_files:
        result = analyze_task_file(task_file, file_map)
        results.append(result)
    
    # Generate report
    features = ['001A-infrastructure', '001-auth', '002-canvas-management', '003-portfolio-dashboard', '004-monthly-review']
    
    print("# Verify Predecessors Report")
    print()
    print("## Summary")
    print("| Feature | Tasks | Unresolved TBDs | Missing Cross-Feature | Status |")
    print("|---------|-------|-----------------|----------------------|--------|")
    
    overall_pass = 0
    overall_fail = 0
    
    for feature in features:
        feature_results = [r for r in results if r.get('feature') == feature]
        task_count = len(feature_results)
        
        total_tbds = sum(len(r.get('unresolved_tbds', [])) for r in feature_results)
        total_missing = sum(len(r.get('missing_predecessors', [])) for r in feature_results)
        
        status = "PASS" if total_tbds == 0 and total_missing == 0 else "FAIL"
        if status == "PASS":
            overall_pass += 1
        else:
            overall_fail += 1
            
        print(f"| {feature} | {task_count} | {total_tbds} | {total_missing} | {status} |")
    
    print()
    print("## Unresolved TBDs")
    print("| Feature | Task | File | Should Be |")
    print("|---------|------|------|-----------|")
    
    all_tbds = []
    for result in results:
        all_tbds.extend(result.get('unresolved_tbds', []))
    
    if all_tbds:
        for tbd in all_tbds:
            print(f"| {tbd['feature']} | {tbd['task']} | {tbd['file']} | {tbd['should_be']} |")
    else:
        print("None")
    
    print()
    print("## Missing Cross-Feature Predecessors")
    print("| Feature | Task | Import | Source Feature | Source Task |")
    print("|---------|------|--------|---------------|-------------|")
    
    all_missing = []
    for result in results:
        all_missing.extend(result.get('missing_predecessors', []))
    
    if all_missing:
        for missing in all_missing:
            print(f"| {missing['feature']} | {missing['task']} | {missing['import']} | {missing['source_feature']} | {missing['source_task']} |")
    else:
        print("None")
    
    print()
    print("## Unresolvable (file not in file-map.md)")
    print("| Feature | Task | Import |")
    print("|---------|------|--------|")
    
    all_unresolvable = []
    for result in results:
        all_unresolvable.extend(result.get('unresolvable_imports', []))
    
    if all_unresolvable:
        for unres in all_unresolvable:
            feature = result.get('feature', 'Unknown')
            task = result.get('task', 'Unknown')
            print(f"| {feature} | {task} | {unres['import']} |")
    else:
        print("None")
    
    print()
    print(f"## Overall: {overall_pass} PASS, {overall_fail} FAIL")

if __name__ == "__main__":
    main()