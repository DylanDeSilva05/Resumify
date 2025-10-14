# Frontend-Backend Integration Guide

This document explains how to integrate your React frontend with the Resumify backend API.

## 🔗 Base Configuration

### API Base URL

```javascript
// In your frontend config
const API_BASE_URL = "http://localhost:8000/api/v1";
```

### Authentication Header

```javascript
// Add to all authenticated requests
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

## 🔐 Authentication Flow

### 1. Login Process

**Frontend Login Function:**
```javascript
const login = async (username, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password
      })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();

    // Store token and user info
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};
```

### 2. Authentication State Management

```javascript
// React context for authentication
import React, { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('accessToken');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    // ... login logic from above
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## 📊 Main CV Analysis Integration

### 1. CV Upload and Analysis (Main Feature)

This is the primary endpoint your dashboard uses:

```javascript
const uploadAndAnalyzeCVs = async (files, jobTitle, jobRequirements) => {
  const formData = new FormData();

  // Add files
  files.forEach(file => {
    formData.append('files', file);
  });

  // Add job information
  formData.append('job_title', jobTitle);
  formData.append('job_requirements', jobRequirements);

  try {
    const response = await fetch(`${API_BASE_URL}/analysis/upload-and-analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Don't set Content-Type for FormData - browser sets it automatically
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Upload failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};
```

### 2. Integration with Your Dashboard Component

Update your `DashboardPage.jsx` to use the real API:

```javascript
// Replace the existing handleJobFormSubmit function
const handleJobFormSubmit = async (e) => {
  e.preventDefault();

  if (uploadedFiles.length === 0) {
    showNotification('Please upload CV files first', 'warning');
    goToStep(1);
    return;
  }

  setIsProcessing(true);

  try {
    // Call the real API
    const results = await uploadAndAnalyzeCVs(
      uploadedFiles,
      jobForm.title,
      jobForm.requirements
    );

    // Update state with real results
    setCandidates({
      total: results.total,
      shortlisted: results.shortlisted,
      rejected: results.rejected
    });

    // Store candidate details for modals
    setCandidateDetails(results.candidates);

    showNotification(`Processed ${results.total} CVs successfully!`, 'success');
    goToStep(3);

  } catch (error) {
    showNotification(`Failed to process CVs: ${error.message}`, 'error');
    console.error('Analysis error:', error);
  } finally {
    setIsProcessing(false);
  }
};
```

### 3. Display Candidate Results

Update your candidate display to show real data:

```javascript
const handleShowCandidates = (status) => {
  // Filter candidates by status
  const filteredCandidates = candidateDetails.filter(
    candidate => candidate.match_status === status
  );

  setModalData({
    status,
    candidates: filteredCandidates
  });
  setShowCandidatesModal(true);
};

// Update the modal table to show real data
<tbody>
  {modalData.candidates.map(candidate => (
    <tr key={candidate.id}>
      <td style={{ fontWeight: 600 }}>{candidate.name}</td>
      <td>{candidate.email || 'N/A'}</td>
      <td><span className="match-percentage">{Math.round(candidate.match_score)}%</span></td>
      <td style={{ maxWidth: '300px' }}>{candidate.summary}</td>
      <td>
        {modalData.status === 'shortlisted' && (
          <button
            className="action-btn primary"
            onClick={() => handleScheduleInterview(candidate)}
          >
            Schedule Interview
          </button>
        )}
      </td>
    </tr>
  ))}
</tbody>
```

## 🗓️ Interview Scheduling Integration

### 1. Schedule Interview API Call

```javascript
const scheduleInterview = async (candidateId, datetime, type) => {
  try {
    const response = await fetch(`${API_BASE_URL}/interviews/schedule`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        candidate_id: candidateId,
        datetime: datetime, // ISO format: "2024-01-15T10:00:00"
        type: type // "video", "phone", or "in-person"
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to schedule interview');
    }

    return await response.json();
  } catch (error) {
    console.error('Interview scheduling error:', error);
    throw error;
  }
};
```

### 2. Update Interview Form Handler

```javascript
const handleInterviewSubmit = async (e) => {
  e.preventDefault();

  setIsProcessing(true);

  try {
    const result = await scheduleInterview(
      selectedCandidate.id,
      interviewForm.datetime,
      interviewForm.type
    );

    showNotification(result.message || `Interview scheduled with ${selectedCandidate.name}!`, 'success');
    setShowEmailModal(false);

  } catch (error) {
    showNotification(`Failed to schedule interview: ${error.message}`, 'error');
  } finally {
    setIsProcessing(false);
  }
};
```

## 👥 User Management Integration

### 1. Get Users List

```javascript
const getUsers = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }

    return await response.json();
  } catch (error) {
    console.error('Get users error:', error);
    throw error;
  }
};
```

### 2. Create New User

```javascript
const createUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create user');
    }

    return await response.json();
  } catch (error) {
    console.error('Create user error:', error);
    throw error;
  }
};
```

## 🔍 API Response Formats

### Authentication Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "hr_manager",
    "email": "hr@company.com",
    "full_name": "HR Manager",
    "user_type": "hr_manager",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### CV Analysis Response
```json
{
  "total": 5,
  "shortlisted": 2,
  "rejected": 2,
  "candidates": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "match_score": 85.5,
      "summary": "Strong technical background with excellent Python skills",
      "strengths": ["Strong technical skill alignment", "Meets experience requirements"],
      "concerns": ["Missing some preferred skills"],
      "match_status": "shortlisted"
    }
  ]
}
```

### Interview Scheduling Response
```json
{
  "message": "Interview scheduled successfully with John Doe",
  "interview_id": 1,
  "candidate": "John Doe",
  "datetime": "2024-01-15T10:00:00Z",
  "type": "video"
}
```

## 🛡️ Error Handling

### 1. Global Error Handler

```javascript
const apiRequest = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    // Handle different HTTP status codes
    if (response.status === 401) {
      // Token expired or invalid
      logout();
      throw new Error('Session expired. Please log in again.');
    }

    if (response.status === 403) {
      throw new Error('You do not have permission to perform this action.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};
```

### 2. Component Error Boundaries

```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## 🔄 Loading States and Progress

### 1. Upload Progress Tracking

```javascript
const uploadWithProgress = async (files, jobTitle, jobRequirements, onProgress) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  formData.append('job_title', jobTitle);
  formData.append('job_requirements', jobRequirements);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const progress = (event.loaded / event.total) * 100;
        onProgress(progress);
      }
    });

    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    };

    xhr.onerror = () => reject(new Error('Upload failed'));

    xhr.open('POST', `${API_BASE_URL}/analysis/upload-and-analyze`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
};
```

### 2. Loading Spinner Component

```javascript
const LoadingSpinner = ({ message = 'Loading...' }) => (
  <div className="loading-container">
    <div className="loading-spinner"></div>
    <p>{message}</p>
  </div>
);

// Usage in your components
{isProcessing && <LoadingSpinner message="Analyzing CVs..." />}
```

## 🌐 Environment Configuration

### 1. Environment Variables

Create `.env.local` in your frontend:

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_API_TIMEOUT=30000

# Feature Flags
REACT_APP_ENABLE_DEBUG=true
REACT_APP_ENABLE_ANALYTICS=false
```

### 2. API Configuration

```javascript
// config/api.js
const config = {
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000,
  enableDebug: process.env.REACT_APP_ENABLE_DEBUG === 'true'
};

export default config;
```

## ✅ Testing Integration

### 1. Test API Connection

```javascript
const testConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/../health`);
    const data = await response.json();
    console.log('Backend status:', data.status);
    return data.status === 'healthy';
  } catch (error) {
    console.error('Backend connection failed:', error);
    return false;
  }
};

// Call this on app startup
useEffect(() => {
  testConnection().then(isHealthy => {
    if (!isHealthy) {
      setNotification('Backend service is unavailable', 'error');
    }
  });
}, []);
```

### 2. Mock Data for Development

```javascript
// For development when backend is not available
const useMockData = process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API;

const analyzeCVs = async (files, jobTitle, requirements) => {
  if (useMockData) {
    // Return mock data for development
    return {
      total: files.length,
      shortlisted: Math.ceil(files.length * 0.3),
      rejected: Math.floor(files.length * 0.5),
      candidates: files.map((file, index) => ({
        id: index + 1,
        name: `Candidate ${index + 1}`,
        email: `candidate${index + 1}@example.com`,
        match_score: Math.random() * 100,
        summary: `Mock candidate analysis for ${file.name}`,
        strengths: ['Strong technical skills'],
        concerns: [],
        match_status: index % 3 === 0 ? 'shortlisted' : 'rejected'
      }))
    };
  }

  // Use real API
  return await uploadAndAnalyzeCVs(files, jobTitle, requirements);
};
```

---

## 🚀 Summary

This integration guide covers:

1. **Authentication**: JWT token management and user sessions
2. **CV Analysis**: The main feature for uploading and analyzing CVs
3. **Interview Scheduling**: Creating interviews with candidates
4. **User Management**: Managing HR team members
5. **Error Handling**: Robust error management and user feedback
6. **Loading States**: Progress indicators and user experience
7. **Testing**: Development tools and mock data support

The backend API is designed to work seamlessly with your existing frontend components. Simply replace the mock functions with the real API calls shown above, and your application will be fully functional with powerful CV parsing and analysis capabilities!