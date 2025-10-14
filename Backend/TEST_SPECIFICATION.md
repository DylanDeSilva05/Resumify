# Resumify Backend - Pytest Test Specification Document

## Table of Contents
1. [Unit Testing - 10 Test Cases](#unit-testing)
2. [Integration Testing - 10 Test Cases](#integration-testing)
3. [Security Testing - 10 Test Cases](#security-testing)
4. [Performance & Load Testing - 10 Test Cases](#performance-load-testing)
5. [Test Organization & Directory Structure](#test-organization)
6. [Running Tests](#running-tests)
7. [CI/CD Integration](#cicd-integration)

---

## Unit Testing - 10 Test Cases

Unit tests verify individual functions and methods in isolation using mocks and fixtures.

| Test ID | Test Objective / Evaluation Criteria | Technique Employed (E, B) | Expected Input | Expected Outcome |
|---------|-------------------------------------|---------------------------|----------------|------------------|
| U-01 | Valid password hashing - verify bcrypt hash generation | E | password="SecurePass123!" | Hash string starts with "$2b$", password verifies successfully |
| U-02 | Invalid password verification - reject wrong password | B | stored_hash="$2b$12$...", password="WrongPass" | verify_password returns False |
| U-03 | Valid JWT token generation for authenticated user | E | user_id=1, email="test@test.com", role="candidate" | JWT token string with valid claims (sub, email, role, exp) |
| U-04 | Expired JWT token validation - reject expired token | B | token=expired_jwt_token, current_time > exp_time | TokenExpiredError raised |
| U-05 | Resume text extraction from PDF - valid PDF file | E | file_path="sample_resume.pdf", file_type="pdf" | Extracted text contains "Experience", "Education", "Skills" |
| U-06 | Resume parsing with missing skills section | B | resume_text="John Doe\nExperience: 5 years" (no skills) | skills=[], warning logged, parsing continues |
| U-07 | Email validation - valid email format | E | email="candidate@resumify.com" | is_valid=True, no exceptions |
| U-08 | Email validation - invalid email format | B | email="invalid-email" | ValidationError raised with "Invalid email format" |
| U-09 | Calculate resume matching score - high match | E | resume_skills=["Python","FastAPI"], job_requirements=["Python","FastAPI","SQL"] | match_score >= 85.0 |
| U-10 | Calculate resume matching score - low match | B | resume_skills=["Java"], job_requirements=["Python","FastAPI","React"] | match_score <= 30.0 |

**Note:** E = Equivalence Partitioning, B = Boundary Value Analysis

**Implementation Location:**
- `tests/unit/test_auth_service.py` - U-01, U-02, U-03, U-04
- `tests/unit/test_cv_parser.py` - U-05, U-06
- `tests/unit/test_validators.py` - U-07, U-08
- `tests/unit/test_cv_analyzer.py` - U-09, U-10

---

## Integration Testing - 10 Test Cases

Integration tests verify the interaction between multiple components, database operations, and API endpoints.

| Test ID | Test Objective / Evaluation Criteria | Technique Employed (E, B) | Expected Input | Expected Outcome |
|---------|-------------------------------------|---------------------------|----------------|------------------|
| I-01 | User registration workflow - create new candidate account | E | POST /api/v1/auth/register {username="john_doe", email="john@test.com", password="Pass123!", role="candidate"} | status_code=201, user created in DB, response contains user_id and email |
| I-02 | User login workflow - successful authentication | E | POST /api/v1/auth/login {username="john_doe", password="Pass123!"} | status_code=200, access_token returned, token_type="bearer" |
| I-03 | Resume upload and analysis pipeline | E | POST /api/v1/upload/resume, file=resume.pdf, user_id=1 | status_code=200, file saved to uploads/, CV analysis record created with parsed data |
| I-04 | Job posting creation by company user | E | POST /api/v1/jobs/create {title="Senior Python Developer", company_id=5, requirements=["Python","FastAPI"]} | status_code=201, job record in DB, job_id returned |
| I-05 | Candidate search with filtering - match job requirements | E | GET /api/v1/candidates/search?skills=Python&experience=5 | status_code=200, filtered list of candidates with Python skill and 5+ years experience |
| I-06 | Interview scheduling - create interview between candidate and company | E | POST /api/v1/interviews/schedule {candidate_id=10, company_id=5, job_id=3, scheduled_time="2025-10-15T14:00:00"} | status_code=201, interview record created, email notifications sent to both parties |
| I-07 | Unauthorized access to protected endpoint | B | GET /api/v1/candidates/123 (no auth token in header) | status_code=401, error="Not authenticated" |
| I-08 | Role-based access control - candidate accessing company-only endpoint | B | GET /api/v1/companies/dashboard (auth token with role="candidate") | status_code=403, error="Insufficient permissions" |
| I-09 | Database transaction rollback on validation error | B | POST /api/v1/jobs/create {title="", company_id=999} (invalid data) | status_code=422, no job record in DB, transaction rolled back |
| I-10 | Resume matching algorithm - full pipeline test | E | candidate_id=10 with skills ["Python","FastAPI"], job_id=3 requires ["Python","Django","SQL"] | match_score calculated, match record created in DB, score between 0-100 |

**Implementation Location:**
- `tests/integration/test_auth_flow.py` - I-01, I-02, I-07, I-08
- `tests/integration/test_resume_upload_flow.py` - I-03
- `tests/integration/test_job_posting_flow.py` - I-04, I-09
- `tests/integration/test_candidate_search.py` - I-05, I-06, I-10

---

## Security Testing - 10 Test Cases

Security tests verify authentication, authorization, input validation, and protection against common vulnerabilities.

| Test ID | Test Objective / Evaluation Criteria | Technique Employed (E, B) | Expected Input | Expected Outcome |
|---------|-------------------------------------|---------------------------|----------------|------------------|
| S-01 | SQL Injection prevention in login endpoint | B | POST /api/v1/auth/login {username="admin' OR '1'='1", password="anything"} | status_code=401, parameterized query prevents injection, no authentication |
| S-02 | XSS prevention in user profile update | B | PUT /api/v1/profile {full_name="<script>alert('XSS')</script>"} | status_code=200, script tags sanitized/escaped, stored as plain text |
| S-03 | JWT token tampering detection | B | GET /api/v1/candidates/me (modified JWT signature) | status_code=401, InvalidSignatureError, access denied |
| S-04 | Brute force protection on login attempts | B | 6 consecutive POST /api/v1/auth/login requests with wrong password | status_code=429 (Too Many Requests) after 5 attempts, account locked for 15 minutes |
| S-05 | File upload validation - reject malicious file types | B | POST /api/v1/upload/resume, file=malicious.exe (disguised as PDF) | status_code=400, error="Invalid file type", file rejected and not saved |
| S-06 | File upload size limit enforcement | B | POST /api/v1/upload/resume, file=large_resume.pdf (15MB) | status_code=413, error="File too large", max size 10MB enforced |
| S-07 | CORS policy enforcement - block unauthorized origin | B | OPTIONS /api/v1/jobs (Origin: http://malicious-site.com) | Access-Control-Allow-Origin not set for unauthorized origin, request blocked |
| S-08 | Password complexity validation | B | POST /api/v1/auth/register {password="12345"} | status_code=422, error="Password must contain uppercase, lowercase, number, and special character" |
| S-09 | Sensitive data exposure in API responses | E | GET /api/v1/users/123 | status_code=200, response excludes password_hash field, only safe fields returned |
| S-10 | Two-Factor Authentication verification | E | POST /api/v1/auth/2fa/verify {user_id=1, code="123456"} | status_code=200 for valid TOTP code, 401 for invalid/expired code |

**Implementation Location:**
- `tests/security/test_sql_injection.py` - S-01
- `tests/security/test_xss_prevention.py` - S-02
- `tests/security/test_jwt_security.py` - S-03, S-10
- `tests/security/test_rate_limiting.py` - S-04
- `tests/security/test_file_upload_security.py` - S-05, S-06, S-07, S-08, S-09

---

## Performance & Load Testing - 10 Test Cases

Performance tests measure response times, throughput, and system behavior under load.

| Test ID | Test Objective / Evaluation Criteria | Technique Employed (E, B) | Expected Input | Expected Outcome |
|---------|-------------------------------------|---------------------------|----------------|------------------|
| P-01 | API response time - single user login | E | 1 concurrent user, POST /api/v1/auth/login | avg response time < 200ms, 95th percentile < 300ms |
| P-02 | API response time - candidate search query | E | 1 concurrent user, GET /api/v1/candidates/search?skills=Python | avg response time < 500ms, query optimized with indexes |
| P-03 | Load test - 100 concurrent user logins | E | 100 concurrent users, POST /api/v1/auth/login (sustained for 60s) | avg response time < 1s, 0% error rate, CPU < 80% |
| P-04 | Load test - 500 concurrent resume uploads | E | 500 concurrent users uploading 2MB PDFs over 2 minutes | avg response time < 5s, all uploads successful, no timeouts |
| P-05 | Stress test - database connection pool exhaustion | B | 1000 concurrent DB queries exceeding pool size (10 connections) | requests queue properly, no connection errors, pool recycles connections |
| P-06 | Resume parsing performance - large file | B | Parse 10MB PDF resume with 50 pages | parsing completes in < 10s, memory usage < 500MB |
| P-07 | Job search performance with large dataset | E | Search query on 100,000 job postings with filters | response time < 1s, pagination works, indexes utilized |
| P-08 | API throughput - sustained request rate | E | 1000 requests/minute for 10 minutes (mixed endpoints) | success rate > 99.5%, avg response time < 1s, no degradation |
| P-09 | Memory leak detection - long-running session | E | 10,000 sequential API requests over 1 hour | memory usage remains stable, no continuous growth, < 1GB RAM |
| P-10 | Cache performance - repeated candidate searches | E | Same GET /api/v1/candidates/search query repeated 100 times | first request: ~500ms, cached requests: < 50ms, 90% cache hit rate |

**Implementation Location:**
- `tests/performance/test_api_response_time.py` - P-01, P-02, P-09
- `tests/performance/test_load_scenarios.py` - P-03, P-04, P-08
- `tests/performance/test_database_performance.py` - P-05, P-07, P-10
- `tests/performance/locustfile.py` - P-03, P-04, P-08 (Locust load testing)

---

## Test Organization & Directory Structure

### Directory Structure

```
Backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared pytest fixtures and configuration
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_auth_service.py
│   │   ├── test_cv_parser.py
│   │   ├── test_cv_analyzer.py
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py
│   │   ├── test_resume_upload_flow.py
│   │   ├── test_job_posting_flow.py
│   │   └── test_candidate_search.py
│   ├── security/
│   │   ├── __init__.py
│   │   ├── test_sql_injection.py
│   │   ├── test_xss_prevention.py
│   │   ├── test_jwt_security.py
│   │   ├── test_rate_limiting.py
│   │   └── test_file_upload_security.py
│   ├── performance/
│   │   ├── __init__.py
│   │   ├── test_api_response_time.py
│   │   ├── test_load_scenarios.py
│   │   ├── test_database_performance.py
│   │   └── locustfile.py         # For Locust load testing
│   └── fixtures/
│       ├── sample_resumes/
│       │   ├── valid_resume.pdf
│       │   ├── resume_no_skills.pdf
│       │   └── large_resume.pdf
│       └── mock_data.py          # Mock data generators
├── pytest.ini
├── requirements-test.txt
└── TEST_SPECIFICATION.md (this file)
```

### Test Data Requirements

**Unit Tests:**
- Mock database sessions using `pytest-mock` or `unittest.mock`
- Sample text strings for parsing tests
- Pre-generated JWT tokens (valid/expired)
- Sample user objects with known attributes

**Integration Tests:**
- Test database (SQLite in-memory or separate test PostgreSQL)
- Sample PDF/DOCX resume files
- Seed data for users, companies, jobs, candidates
- Mock SMTP server for email testing

**Security Tests:**
- Malicious input strings (SQL injection patterns, XSS payloads)
- Invalid file types (executables, scripts)
- Tampered JWT tokens
- Large payloads for DoS testing

**Performance Tests:**
- Large dataset of users/jobs/candidates (10K+ records)
- Multiple resume files of various sizes
- Load testing tools (Locust, pytest-benchmark)

---

## Running Tests

### Install Test Dependencies

Install test dependencies:
```bash
cd Backend
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/security/
pytest tests/performance/

# Run with markers
pytest -m unit
pytest -m "security or performance"

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run specific test case
pytest tests/unit/test_auth_service.py::TestPasswordHashing::test_password_hash_generation

# Run tests in parallel (install pytest-xdist)
pytest -n auto

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

### Load Testing with Locust

```bash
# Start Locust web interface
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run headless load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless
```

---

## CI/CD Integration

### GitHub Actions

A GitHub Actions workflow file is provided in `.github/workflows/test.yml` that:
- Runs on every push and pull request
- Tests against multiple Python versions (3.9, 3.10, 3.11)
- Executes all test categories
- Generates coverage reports
- Uploads results to Codecov
- Runs security scans with Bandit

### Pre-commit Hooks

Optional: Set up pre-commit hooks to run unit tests before each commit:

```bash
pip install pre-commit
pre-commit install
```

### Test Execution Summary

| Command | Purpose | When to Run |
|---------|---------|-------------|
| `pytest` | Run all tests | Before every commit |
| `pytest -m unit` | Run unit tests only | During development |
| `pytest -m integration` | Run integration tests | Before push |
| `pytest -m security` | Run security tests | Before release |
| `pytest --cov=app` | Run with coverage | Weekly/before PR |
| `locust -f locustfile.py` | Load testing | Before production deploy |

---

## Summary

This test specification provides:

- **40 detailed test cases** across 4 testing categories
- **Pytest-based implementation** with fixtures and mocks
- **Realistic scenarios** for Resumify system (auth, resume parsing, job matching)
- **Organized directory structure** separating test types
- **Complete working code** in separate test files
- **CI/CD integration** with GitHub Actions
- **Performance testing** with both pytest and Locust

All tests follow the specified table format with Test ID, Objective, Technique (E/B), Input, and Expected Outcome.
