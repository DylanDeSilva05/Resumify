"""
Shared pytest fixtures for all test suites
Location: Backend/tests/conftest.py

This file contains reusable fixtures for:
- Database setup (in-memory SQLite for testing)
- Test client configuration
- Mock user creation
- Authentication headers
- Sample data generation
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator, Dict

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app  # main.py is at Backend root level
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.company import Company


# Test database configuration (SQLite in-memory)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """
    Create a test database engine with SQLite in-memory
    Scope: function - new database for each test
    """
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create a test database session
    Scope: function - new session for each test
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI test client with database dependency override
    Scope: function - new client for each test
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def sample_company(db_session) -> Company:
    """
    Create a sample company for testing
    """
    company = Company(
        company_name="Test Company Inc",
        contact_email="info@testcompany.com",
        contact_phone="+1-555-0100",
        is_active=True,
        subscription_tier="basic"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def sample_candidate_user(db_session, sample_company) -> User:
    """
    Create a sample candidate user for testing
    Password: TestPass123!
    """
    user = User(
        username="test_candidate",
        email="candidate@test.com",
        hashed_password=get_password_hash("TestPass123!"),
        full_name="Test Candidate",
        role=UserRole.COMPANY_USER,
        is_active=True,
        company_id=sample_company.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_company_admin(db_session, sample_company) -> User:
    """
    Create a sample company admin user for testing
    Password: AdminPass123!
    """
    user = User(
        username="test_company_admin",
        email="admin@testcompany.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Test Company Admin",
        role=UserRole.COMPANY_ADMIN,
        is_active=True,
        company_id=sample_company.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_recruiter(db_session, sample_company) -> User:
    """
    Create a sample recruiter user for testing
    Password: RecruiterPass123!
    """
    user = User(
        username="test_recruiter",
        email="recruiter@testcompany.com",
        hashed_password=get_password_hash("RecruiterPass123!"),
        full_name="Test Recruiter",
        role=UserRole.RECRUITER,
        is_active=True,
        company_id=sample_company.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_super_admin(db_session) -> User:
    """
    Create a sample super admin user for testing
    Password: SuperAdmin123!
    Note: Super admin has no company_id
    """
    user = User(
        username="test_super_admin",
        email="superadmin@resumify.com",
        hashed_password=get_password_hash("SuperAdmin123!"),
        full_name="Test Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        company_id=None  # Super admin doesn't belong to a company
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_candidate(client, sample_candidate_user) -> Dict[str, str]:
    """
    Generate authentication headers for candidate user
    Returns: {"Authorization": "Bearer <token>"}
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_candidate", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Fallback: create token directly
        token = create_access_token(subject=sample_candidate_user.id)
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_company_admin(client, sample_company_admin) -> Dict[str, str]:
    """
    Generate authentication headers for company admin user
    Returns: {"Authorization": "Bearer <token>"}
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_company_admin", "password": "AdminPass123!"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Fallback: create token directly
        token = create_access_token(subject=sample_company_admin.id)
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_recruiter(client, sample_recruiter) -> Dict[str, str]:
    """
    Generate authentication headers for recruiter user
    Returns: {"Authorization": "Bearer <token>"}
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_recruiter", "password": "RecruiterPass123!"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Fallback: create token directly
        token = create_access_token(subject=sample_recruiter.id)
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_super_admin(client, sample_super_admin) -> Dict[str, str]:
    """
    Generate authentication headers for super admin user
    Returns: {"Authorization": "Bearer <token>"}
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_super_admin", "password": "SuperAdmin123!"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Fallback: create token directly
        token = create_access_token(subject=sample_super_admin.id)
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_resume_text() -> str:
    """
    Sample resume text for parsing tests
    """
    return """
    John Doe
    Software Engineer
    john.doe@email.com | +1-555-0123

    EXPERIENCE
    Senior Python Developer at Tech Corp (2020-2023)
    - Developed REST APIs using FastAPI and Django
    - Implemented CI/CD pipelines with GitHub Actions
    - Led team of 5 developers

    Python Developer at StartupXYZ (2018-2020)
    - Built microservices architecture
    - Worked with PostgreSQL and Redis

    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2014-2018
    GPA: 3.8/4.0

    SKILLS
    Programming: Python, JavaScript, SQL
    Frameworks: FastAPI, Django, React
    Tools: Docker, Kubernetes, Git
    Databases: PostgreSQL, MongoDB, Redis
    """


@pytest.fixture
def sample_resume_no_skills() -> str:
    """
    Sample resume text without skills section (for boundary testing)
    """
    return """
    Jane Smith
    Marketing Manager
    jane.smith@email.com

    EXPERIENCE
    Marketing Lead at Company ABC (2019-2023)
    - Managed marketing campaigns
    - Increased brand awareness by 40%

    EDUCATION
    MBA in Marketing, Business School, 2017-2019
    """


@pytest.fixture
def sample_job_requirements() -> list:
    """
    Sample job requirements for matching tests
    """
    return ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"]


@pytest.fixture
def mock_pdf_file():
    """
    Create a mock PDF file for testing file uploads
    Note: This is a minimal mock. For real PDF testing, use actual test files.
    """
    from io import BytesIO

    # Create a minimal PDF-like structure
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    return BytesIO(pdf_content)


@pytest.fixture(scope="session")
def test_config():
    """
    Test configuration settings
    Scope: session - shared across all tests
    """
    return {
        "test_mode": True,
        "database_url": SQLALCHEMY_TEST_DATABASE_URL,
        "api_prefix": "/api/v1",
        "test_user_password": "TestPass123!",
        "jwt_algorithm": "HS256",
    }


# Pytest configuration hooks
def pytest_configure(config):
    """
    Pytest configuration hook
    Add custom markers
    """
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


@pytest.fixture(autouse=True)
def reset_database(db_session):
    """
    Auto-use fixture to ensure database is clean before each test
    """
    yield
    # Cleanup happens automatically in db_session fixture
