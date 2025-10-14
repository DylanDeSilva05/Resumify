# Resumify Backend API

AI-Powered HR Recruitment Platform Backend - A comprehensive FastAPI-based solution for CV parsing, candidate matching, and interview management.

## 🚀 Features

### Core Functionality
- **CV Upload & Parsing**: Support for PDF, DOC, DOCX files with structured data extraction
- **AI-Powered Matching**: Intelligent candidate-job matching using NLP and machine learning
- **Authentication**: JWT-based authentication with role-based access control
- **Interview Scheduling**: Complete interview management with email notifications
- **User Management**: HR team member management with different permission levels

### Technical Highlights
- **FastAPI Framework**: Modern, fast, and type-hinted API development
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Asynchronous Processing**: Background tasks with Celery and Redis
- **Natural Language Processing**: Advanced text analysis with spaCy
- **File Processing**: Secure file upload and parsing capabilities
- **Production Ready**: Comprehensive error handling, logging, and validation

## 📁 Project Structure

```
Backend/
├── app/
│   ├── api/                    # API routes and endpoints
│   │   ├── api_v1/
│   │   │   ├── endpoints/      # Individual endpoint modules
│   │   │   │   ├── auth.py     # Authentication endpoints
│   │   │   │   ├── users.py    # User management
│   │   │   │   ├── analysis.py # CV analysis (main feature)
│   │   │   │   ├── candidates.py # Candidate management
│   │   │   │   ├── jobs.py     # Job posting management
│   │   │   │   └── interviews.py # Interview scheduling
│   │   │   └── api.py          # API router
│   │   └── deps.py             # API dependencies
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database setup
│   │   ├── security.py         # JWT and password handling
│   │   └── exceptions.py       # Custom exceptions
│   ├── models/                 # Database models
│   │   ├── user.py             # User model
│   │   ├── candidate.py        # Candidate model
│   │   ├── job_posting.py      # Job posting model
│   │   ├── cv_analysis.py      # CV analysis results
│   │   └── interview.py        # Interview model
│   ├── schemas/                # Pydantic models
│   │   ├── user.py             # User schemas
│   │   ├── candidate.py        # Candidate schemas
│   │   ├── job_posting.py      # Job posting schemas
│   │   ├── cv_analysis.py      # Analysis schemas
│   │   └── interview.py        # Interview schemas
│   ├── services/               # Business logic
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── cv_parser.py        # CV parsing service
│   │   ├── cv_analyzer.py      # CV analysis service
│   │   └── nlp_service.py      # NLP processing
│   └── utils/                  # Utility functions
│       └── file_utils.py       # File handling utilities
├── uploads/                    # File upload directory
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (for background tasks)

### 1. Clone and Setup Environment

```bash
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL and create database
createdb resumify_db

# Update database URL in .env file
DATABASE_URL=postgresql://username:password@localhost:5432/resumify_db
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Update configuration in .env file
```

### 4. Install NLP Model

```bash
# Download spaCy English model
python -m spacy download en_core_web_md
```

### 5. Run the Application

```bash
# Development server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/token` - OAuth2 compatible login

### User Management
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user (HR Manager only)
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### CV Analysis (Main Feature)
- `POST /api/v1/analysis/upload-and-analyze` - **Upload CVs and analyze**
- `POST /api/v1/analysis/parse-requirements` - Parse job requirements
- `GET /api/v1/analysis/results/{analysis_id}` - Get analysis results
- `GET /api/v1/analysis/candidates/{status}` - Get candidates by status

### Candidate Management
- `GET /api/v1/candidates/` - List candidates
- `GET /api/v1/candidates/{candidate_id}` - Get candidate details
- `PUT /api/v1/candidates/{candidate_id}` - Update candidate
- `DELETE /api/v1/candidates/{candidate_id}` - Delete candidate

### Job Postings
- `GET /api/v1/jobs/` - List job postings
- `POST /api/v1/jobs/` - Create job posting
- `GET /api/v1/jobs/{job_id}` - Get job details
- `PUT /api/v1/jobs/{job_id}` - Update job posting
- `DELETE /api/v1/jobs/{job_id}` - Delete job posting

### Interviews
- `GET /api/v1/interviews/` - List interviews
- `POST /api/v1/interviews/` - Schedule interview
- `POST /api/v1/interviews/schedule` - Simple interview scheduling
- `GET /api/v1/interviews/{interview_id}` - Get interview details
- `PUT /api/v1/interviews/{interview_id}` - Update interview
- `DELETE /api/v1/interviews/{interview_id}` - Cancel interview

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/resumify_db

# JWT Security
SECRET_KEY=your_super_secret_jwt_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,doc,docx

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379/0

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 🎯 Main CV Analysis Workflow

The core functionality is handled by the `/api/v1/analysis/upload-and-analyze` endpoint:

### 1. CV Upload
- Accepts multiple files (PDF, DOC, DOCX)
- Validates file types and sizes
- Stores files securely

### 2. Job Requirements Processing
- Accepts job title and natural language requirements
- Uses NLP to extract structured requirements:
  - Required/preferred technical skills
  - Education requirements
  - Experience requirements
  - Soft skills

### 3. CV Parsing
- Extracts text from uploaded files
- Parses structured information:
  - Personal information (name, email, phone)
  - Education history
  - Work experience
  - Technical and soft skills
  - Certifications and languages

### 4. Candidate Matching
- Analyzes each candidate against job requirements
- Calculates matching scores for:
  - Technical skills (35% weight)
  - Experience (25% weight)
  - Education (20% weight)
  - Soft skills (20% weight)
- Generates AI-powered insights and recommendations

### 5. Results Classification
- **Shortlisted**: Overall score ≥ 70%
- **Pending**: Overall score 50-69%
- **Rejected**: Overall score < 50%

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/upload-and-analyze" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "files=@cv1.pdf" \
  -F "files=@cv2.pdf" \
  -F "job_title=Senior Software Developer" \
  -F "job_requirements=We are looking for a Senior Software Developer with 3-5 years of experience in Python, React, and SQL databases. Bachelor's degree in Computer Science required."
```

### Example Response

```json
{
  "total": 10,
  "shortlisted": 3,
  "rejected": 5,
  "candidates": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "match_score": 85.5,
      "summary": "Strong technical background with excellent Python and React skills",
      "strengths": ["Strong technical skill alignment", "Meets experience requirements"],
      "concerns": [],
      "match_status": "shortlisted"
    }
  ]
}
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. Login with credentials to get access token
2. Include token in Authorization header: `Bearer YOUR_TOKEN`
3. Tokens expire after 30 minutes (configurable)

### User Roles
- **HR Manager**: Full access to all features
- **HR Team**: Read-only access to candidates and analyses

## 🚀 Frontend Integration

This backend is designed to work seamlessly with the provided React frontend:

### Key Integration Points
1. **Authentication**: Compatible with frontend login flow
2. **CV Upload**: Handles multiple file upload from dashboard
3. **Real-time Analysis**: Provides progress and results
4. **Interview Scheduling**: Supports frontend scheduling workflow

### CORS Configuration
Configure `BACKEND_CORS_ORIGINS` in `.env` to match your frontend URL.

## 📊 Database Schema

### Key Tables
- **users**: HR team members with authentication
- **candidates**: Parsed CV information and metadata
- **job_postings**: Job requirements and matching criteria
- **cv_analyses**: Matching results and AI insights
- **interviews**: Interview scheduling and management

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Test API endpoints
curl -X GET "http://localhost:8000/health"
```

## 📝 Development Notes

### Adding New Features
1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Create service in `app/services/`
4. Create endpoints in `app/api/api_v1/endpoints/`
5. Update API router in `app/api/api_v1/api.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Document functions with docstrings
- Handle errors appropriately

## 🐳 Production Deployment

### Docker Support
```bash
# Build Docker image
docker build -t resumify-api .

# Run container
docker run -p 8000:8000 resumify-api
```

### Environment Setup
- Use production database
- Set secure `SECRET_KEY`
- Configure email settings for notifications
- Set up Redis for background tasks
- Configure proper CORS origins

## 🤝 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure all environment variables are configured correctly

---

**Note**: This backend provides a complete, production-ready foundation for an AI-powered HR recruitment platform. The CV parsing and analysis functionality is modular and can be extended with additional AI models and features as needed.