# Resumify Backend - Testing Quick Start Guide

## Quick Setup

### 1. Install Test Dependencies

```bash
cd Backend
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html
```

### 3. Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Security tests
pytest tests/security/ -v

# Performance tests (excluding slow tests)
pytest tests/performance/ -v -m "not slow"
```

## Test Organization

```
Backend/tests/
├── unit/               # U-01 to U-10 (Unit Tests)
├── integration/        # I-01 to I-10 (Integration Tests)
├── security/           # S-01 to S-10 (Security Tests)
└── performance/        # P-01 to P-10 (Performance Tests)
```

## Common Commands

```bash
# Run specific test file
pytest tests/unit/test_auth_service.py -v

# Run specific test function
pytest tests/unit/test_auth_service.py::TestPasswordHashing::test_password_hash_generation -v

# Run tests matching a keyword
pytest -k "login" -v

# Run tests with detailed output
pytest -vv

# Run tests in parallel (faster)
pytest -n auto

# Stop at first failure
pytest -x
```

## Load Testing with Locust

```bash
# Start Locust web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Then open http://localhost:8089 in browser

# Run headless load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless
```

## Coverage Reports

After running tests with coverage:

```bash
# View HTML coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

## CI/CD Integration

Tests run automatically on GitHub Actions for:
- Every push to main/develop branches
- Every pull request
- Tests against Python 3.9, 3.10, and 3.11

## Test Case Reference

See `TEST_SPECIFICATION.md` for complete documentation of all 40 test cases across:
- Unit Testing (10 cases)
- Integration Testing (10 cases)
- Security Testing (10 cases)
- Performance & Load Testing (10 cases)

## Troubleshooting

### Tests fail with import errors
```bash
# Ensure you're in Backend directory
cd Backend

# Reinstall dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Database errors
Tests use SQLite in-memory database. No additional setup required.

### Performance tests timeout
Performance tests may be slow. Run without slow tests:
```bash
pytest tests/performance/ -m "not slow"
```

## Next Steps

1. Review `TEST_SPECIFICATION.md` for detailed test case specifications
2. Run tests locally before committing
3. Check coverage report to identify untested code
4. Add new tests as you develop new features

Happy Testing! 🧪
