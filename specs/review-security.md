# Security Review Report

## Executive Summary

This security review identified **15 security issues** across the Canvas FastAPI + React application, ranging from Critical to Low severity. The most critical issues involve hardcoded secrets, SQL injection vulnerabilities, and missing input validation. The application demonstrates good security practices in authentication and authorization but requires immediate attention to several high-risk vulnerabilities.

## Critical Issues

### SEVERITY: Critical
**FILE:** .env.dev  
**LINE:** 3  
**FEATURE:** 001A-infrastructure  
**TASK:** T-010  
**ISSUE:** Hardcoded secret key in development environment file  
**RATIONALE:** The secret key "dev-secret-key-change-in-production" is hardcoded and exposed in version control. This key is used for JWT signing and could allow attackers to forge authentication tokens.

### SEVERITY: Critical
**FILE:** backend/canvas/services/canvas_service.py  
**LINE:** 142-150  
**FEATURE:** 002-canvas-management  
**TASK:** T-012  
**ISSUE:** SQL injection vulnerability in reorder_theses method  
**RATIONALE:** Direct SQL execution with user-controlled data via text() without proper parameterization. The thesis_orders list contains user input that could be manipulated to inject malicious SQL.

### SEVERITY: Critical
**FILE:** backend/canvas/portfolio/service.py  
**LINE:** 35-50  
**FEATURE:** 003-portfolio-dashboard  
**TASK:** T-005  
**ISSUE:** SQL injection vulnerability in portfolio summary query  
**RATIONALE:** Dynamic SQL construction with user-controlled filter parameters. The where_conditions and params could be manipulated to inject SQL, especially in the health_status filtering.

## High Severity Issues

### SEVERITY: High
**FILE:** backend/canvas/auth/service.py  
**LINE:** 89  
**FEATURE:** 001-auth  
**TASK:** T-013  
**ISSUE:** Incomplete account lockout check with potential timing attack  
**RATIONALE:** The is_account_locked method has a syntax error (user.locked_until instead of user.locked_until) and the authentication flow could leak information about account existence through timing differences.

### SEVERITY: High
**FILE:** backend/canvas/routes/attachment.py  
**LINE:** 25-35  
**FEATURE:** 002-canvas-management  
**TASK:** T-018  
**ISSUE:** Path traversal vulnerability in file upload  
**RATIONALE:** The AttachmentService._generate_storage_path method uses user-controlled filename without proper sanitization, potentially allowing directory traversal attacks to write files outside the intended upload directory.

### SEVERITY: High
**FILE:** backend/canvas/auth/routes.py  
**LINE:** 85-95  
**FEATURE:** 001-auth  
**TASK:** T-016  
**ISSUE:** Insecure cookie configuration in development  
**RATIONALE:** The refresh token cookie is set with secure=True but the application runs on HTTP in development, making the cookie inaccessible and breaking authentication flow.

### SEVERITY: High
**FILE:** frontend/src/api/client.ts  
**LINE:** 3  
**FEATURE:** 001A-infrastructure  
**TASK:** T-011  
**ISSUE:** Hardcoded API endpoint URL  
**RATIONALE:** The baseURL is hardcoded to localhost:8000, exposing internal infrastructure details and making the application vulnerable to SSRF attacks if deployed without proper configuration.

## Medium Severity Issues

### SEVERITY: Medium
**FILE:** backend/canvas/main.py  
**LINE:** 25-30  
**FEATURE:** 001A-infrastructure  
**TASK:** T-008  
**ISSUE:** Overly permissive CORS configuration  
**RATIONALE:** The middleware adds "access-control-allow-origin: *" header unconditionally, bypassing the configured CORS origins and allowing any domain to make requests.

### SEVERITY: Medium
**FILE:** backend/canvas/auth/routes.py  
**LINE:** 140-150  
**FEATURE:** 001-auth  
**TASK:** T-016  
**ISSUE:** Missing rate limiting on authentication endpoints  
**RATIONALE:** No rate limiting on login, refresh, or registration endpoints allows brute force attacks and account enumeration.

### SEVERITY: Medium
**FILE:** backend/canvas/services/attachment_service.py  
**LINE:** 45-55  
**FEATURE:** 002-canvas-management  
**TASK:** T-013  
**ISSUE:** Insufficient file type validation  
**RATIONALE:** Content-Type header validation only, which can be easily spoofed. No magic number validation to verify actual file content matches declared type.

### SEVERITY: Medium
**FILE:** backend/canvas/reviews/router.py  
**LINE:** 15-25  
**FEATURE:** 004-monthly-review  
**TASK:** T-014  
**ISSUE:** Authorization bypass through string role comparison  
**RATIONALE:** Role checking uses string comparison instead of enum, potentially allowing authorization bypass if role values are manipulated.

### SEVERITY: Medium
**FILE:** backend/canvas/portfolio/service.py  
**LINE:** 65-70  
**FEATURE:** 003-portfolio-dashboard  
**TASK:** T-005  
**ISSUE:** HTML entity encoding insufficient for XSS prevention  
**RATIONALE:** Using html.escape() alone is insufficient for XSS prevention in all contexts. Need proper output encoding based on context (HTML, JavaScript, CSS, URL).

## Low Severity Issues

### SEVERITY: Low
**FILE:** docker-compose.yml  
**LINE:** 6-8  
**FEATURE:** 001A-infrastructure  
**TASK:** T-010  
**ISSUE:** Weak database credentials in development  
**RATIONALE:** Default database password "canvas_dev" is weak and predictable, though acceptable for development environments.

### SEVERITY: Low
**FILE:** backend/canvas/main.py  
**LINE:** 50-60  
**FEATURE:** 001A-infrastructure  
**TASK:** T-008  
**ISSUE:** Information disclosure in error responses  
**RATIONALE:** Exception handler logs full stack traces and includes request IDs in error responses, potentially leaking sensitive information about application structure.

### SEVERITY: Low
**FILE:** frontend/src/auth/AuthContext.tsx  
**LINE:** 15-20  
**FEATURE:** 001-auth  
**TASK:** T-017  
**ISSUE:** Access token stored in memory without protection  
**RATIONALE:** Access token stored in plain JavaScript variable is vulnerable to XSS attacks. Consider using secure storage mechanisms or shorter token lifetimes.

## Security Hygiene Issues

### Missing Security Headers
- No Content Security Policy (CSP) headers
- Missing X-Frame-Options header
- No X-Content-Type-Options header
- Missing Referrer-Policy header

### Input Validation Gaps
- Insufficient validation on file uploads beyond size and type
- Missing input sanitization in several endpoints
- No validation of UUID format consistency

### Logging and Monitoring
- No security event logging (failed logins, privilege escalations)
- Missing audit trail for sensitive operations
- No monitoring for suspicious patterns

## Recommendations

### Immediate Actions (Critical/High)
1. **Replace hardcoded secrets** with environment variables
2. **Fix SQL injection vulnerabilities** by using parameterized queries
3. **Implement proper path sanitization** for file uploads
4. **Fix authentication cookie configuration** for development
5. **Add rate limiting** to authentication endpoints

### Short-term Improvements (Medium)
1. **Implement proper CORS configuration** without wildcard bypass
2. **Add magic number validation** for file uploads
3. **Use enum-based role checking** consistently
4. **Implement context-aware output encoding**

### Long-term Security Enhancements (Low)
1. **Add comprehensive security headers**
2. **Implement security event logging**
3. **Add input validation middleware**
4. **Consider token storage alternatives**

## Conclusion

The Canvas application has a solid foundation with proper authentication and authorization patterns, but requires immediate attention to several critical security vulnerabilities. The SQL injection issues and hardcoded secrets pose the highest risk and should be addressed before any production deployment.