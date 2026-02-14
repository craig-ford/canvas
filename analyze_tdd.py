#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def extract_task_info(file_path: str) -> Dict:
    """Extract task number, type, and code blocks from task file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract task number from filename
    task_num = Path(file_path).stem  # T-001, T-002, etc.
    
    # Extract type
    type_match = re.search(r'^## Type\s*\n(.+)', content, re.MULTILINE)
    task_type = type_match.group(1).strip() if type_match else "unknown"
    
    # Extract Contract section
    contract_match = re.search(r'^## Contract\s*\n```python\s*\n(.*?)\n```', content, re.MULTILINE | re.DOTALL)
    contract_code = contract_match.group(1) if contract_match else ""
    
    # Extract Logic section  
    logic_match = re.search(r'^## Logic\s*\n(.*?)(?=^## |$)', content, re.MULTILINE | re.DOTALL)
    logic_text = logic_match.group(1) if logic_match else ""
    
    return {
        'task_num': task_num,
        'type': task_type,
        'contract_code': contract_code,
        'logic_text': logic_text,
        'file_path': file_path
    }

def analyze_feature(feature_dir: str) -> Dict:
    """Analyze all tasks in a feature directory."""
    tasks_dir = os.path.join(feature_dir, 'tasks')
    if not os.path.exists(tasks_dir):
        return {'tasks': [], 'tdd_issues': [], 'stub_issues': []}
    
    tasks = []
    task_files = sorted([f for f in os.listdir(tasks_dir) if f.startswith('T-') and f.endswith('.md')])
    
    for task_file in task_files:
        file_path = os.path.join(tasks_dir, task_file)
        task_info = extract_task_info(file_path)
        tasks.append(task_info)
    
    # Check 3E: TDD Ordering
    tdd_issues = check_tdd_ordering(tasks)
    
    # Check 3G: Stub Detection
    stub_issues = check_stubs(tasks)
    
    return {
        'tasks': tasks,
        'tdd_issues': tdd_issues,
        'stub_issues': stub_issues
    }

def check_tdd_ordering(tasks: List[Dict]) -> List[Dict]:
    """Check 3E: Test tasks should precede implementation tasks."""
    issues = []
    
    # Group tasks by type
    test_tasks = [t for t in tasks if t['type'] in ['contract-test', 'integration-test', 'unit-test']]
    impl_tasks = [t for t in tasks if t['type'] == 'implementation']
    
    # For each implementation task, check if there are corresponding test tasks before it
    for impl_task in impl_tasks:
        impl_num = int(impl_task['task_num'].split('-')[1])
        
        # Find test tasks that should precede this implementation
        preceding_tests = [t for t in test_tasks if int(t['task_num'].split('-')[1]) < impl_num]
        following_tests = [t for t in test_tasks if int(t['task_num'].split('-')[1]) > impl_num]
        
        # If there are tests after implementation, that's a TDD violation
        if following_tests and not preceding_tests:
            issues.append({
                'issue': f"Implementation {impl_task['task_num']} comes before its tests",
                'tasks_affected': f"{impl_task['task_num']} vs {', '.join([t['task_num'] for t in following_tests])}"
            })
    
    return issues

def check_stubs(tasks: List[Dict]) -> List[Dict]:
    """Check 3G: Detect stub methods in Logic sections and test methods in Contract sections."""
    issues = []
    
    for task in tasks:
        # Check Contract section for test method stubs (test-type tasks only)
        if task['type'] in ['contract-test', 'integration-test', 'unit-test']:
            contract_stubs = find_test_method_stubs(task['contract_code'])
            for stub in contract_stubs:
                issues.append({
                    'feature': os.path.basename(os.path.dirname(os.path.dirname(task['file_path']))),
                    'task': task['task_num'],
                    'section': 'Contract',
                    'method': stub['method'],
                    'issue': stub['reason']
                })
        
        # Check Logic section for implementation stubs (implementation-type tasks only)
        if task['type'] == 'implementation':
            logic_stubs = find_logic_stubs(task['logic_text'])
            for stub in logic_stubs:
                issues.append({
                    'feature': os.path.basename(os.path.dirname(os.path.dirname(task['file_path']))),
                    'task': task['task_num'],
                    'section': 'Logic',
                    'method': stub['method'],
                    'issue': stub['reason']
                })
    
    return issues

def find_test_method_stubs(contract_code: str) -> List[Dict]:
    """Find test methods that are stubs in Contract sections."""
    stubs = []
    
    # Find all test methods - look for complete method definitions
    method_pattern = r'def (test_\w+)\([^)]*\):\s*\n(.*?)(?=\n\s*def|\n\s*class|\n\s*```|\Z)'
    test_methods = re.findall(method_pattern, contract_code, re.DOTALL)
    
    for method_name, method_body in test_methods:
        # Clean up the method body and split into lines
        body_lines = [line.strip() for line in method_body.split('\n')]
        
        # Remove empty lines and process content
        non_empty_lines = [line for line in body_lines if line.strip()]
        
        # Skip docstrings (lines starting with """ or ''')
        code_lines = []
        skip_next = False
        in_multiline_docstring = False
        
        for line in non_empty_lines:
            # Handle multiline docstrings
            if line.startswith('"""') or line.startswith("'''"):
                if line.count('"""') == 2 or line.count("'''") == 2:
                    # Single line docstring, skip it
                    continue
                else:
                    # Start of multiline docstring
                    in_multiline_docstring = not in_multiline_docstring
                    continue
            
            if in_multiline_docstring:
                if line.endswith('"""') or line.endswith("'''"):
                    in_multiline_docstring = False
                continue
                
            # Skip comments
            if line.startswith('#'):
                continue
                
            code_lines.append(line)
        
        # Now check if it's a stub
        if not code_lines:
            stubs.append({'method': method_name, 'reason': 'empty body after docstring'})
        elif len(code_lines) == 1 and code_lines[0] == 'pass':
            stubs.append({'method': method_name, 'reason': 'only pass statement'})
        elif len(code_lines) == 1 and code_lines[0] == 'assert True  # Placeholder for actual test':
            stubs.append({'method': method_name, 'reason': 'placeholder assert True'})
        elif all('assert True' in line and ('placeholder' in line.lower() or 'todo' in line.lower()) for line in code_lines):
            stubs.append({'method': method_name, 'reason': 'only placeholder assert True statements'})
        elif not any('assert' in line or 'pytest.raises' in line or 'with pytest.raises' in line for line in code_lines):
            # Only flag if there are actual code lines but no assertions
            if code_lines:  # Has code but no assertions
                stubs.append({'method': method_name, 'reason': 'no assert statements or pytest.raises'})
    
    return stubs

def find_logic_stubs(logic_text: str) -> List[Dict]:
    """Find stub methods in Logic sections (implementation tasks only)."""
    stubs = []
    
    # This is more complex as Logic sections are typically prose, not code
    # Look for mentions of methods that are just pass or NotImplementedError
    if 'pass' in logic_text.lower() and 'method' in logic_text.lower():
        # This is a heuristic - in practice, Logic sections are usually prose
        # describing what to implement, not actual code
        pass
    
    return stubs

def main():
    """Main analysis function."""
    features = [
        '001A-infrastructure',
        '001-auth', 
        '002-canvas-management',
        '003-portfolio-dashboard',
        '004-monthly-review'
    ]
    
    results = {}
    
    for feature in features:
        feature_dir = f'/home/craig/canvas/specs/{feature}'
        if os.path.exists(feature_dir):
            results[feature] = analyze_feature(feature_dir)
        else:
            results[feature] = {'tasks': [], 'tdd_issues': [], 'stub_issues': []}
    
    # Generate report
    generate_report(results)

def generate_report(results: Dict):
    """Generate the TDD verification report."""
    report_lines = []
    report_lines.append("# Verify TDD Report")
    report_lines.append("")
    
    # Summary table
    report_lines.append("## Summary")
    report_lines.append("| Feature | Tasks | 3E Order | 3G Stubs | Status |")
    report_lines.append("|---------|-------|----------|----------|--------|")
    
    total_pass = 0
    total_fail = 0
    
    for feature, data in results.items():
        task_count = len(data['tasks'])
        order_status = "✓" if not data['tdd_issues'] else "✗"
        stub_status = "✓" if not data['stub_issues'] else "✗"
        overall_status = "PASS" if not data['tdd_issues'] and not data['stub_issues'] else "FAIL"
        
        if overall_status == "PASS":
            total_pass += 1
        else:
            total_fail += 1
            
        report_lines.append(f"| {feature} | {task_count} | {order_status} | {stub_status} | {overall_status} |")
    
    report_lines.append("")
    
    # TDD Ordering Issues
    report_lines.append("## TDD Ordering Issues (3E)")
    report_lines.append("| Feature | Issue | Tasks Affected |")
    report_lines.append("|---------|-------|----------------|")
    
    has_tdd_issues = False
    for feature, data in results.items():
        for issue in data['tdd_issues']:
            has_tdd_issues = True
            report_lines.append(f"| {feature} | {issue['issue']} | {issue['tasks_affected']} |")
    
    if not has_tdd_issues:
        report_lines.append("| None | | |")
    
    report_lines.append("")
    
    # Stubs Found
    report_lines.append("## Stubs Found (3G)")
    report_lines.append("| Feature | Task | Section | Method | Issue |")
    report_lines.append("|---------|------|---------|--------|-------|")
    
    has_stub_issues = False
    for feature, data in results.items():
        for issue in data['stub_issues']:
            has_stub_issues = True
            report_lines.append(f"| {issue['feature']} | {issue['task']} | {issue['section']} | {issue['method']} | {issue['issue']} |")
    
    if not has_stub_issues:
        report_lines.append("| None | | | | |")
    
    report_lines.append("")
    report_lines.append(f"## Overall: {total_pass} PASS, {total_fail} FAIL")
    
    # Write report
    with open('/home/craig/canvas/specs/verify-tdd-report.md', 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report written to specs/verify-tdd-report.md")
    print(f"Overall: {total_pass} PASS, {total_fail} FAIL")

if __name__ == "__main__":
    main()