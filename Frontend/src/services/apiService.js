const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  // Helper method to handle 401 errors
  handleUnauthorized() {
    // Clear token
    localStorage.removeItem('authToken');
    // Redirect to login
    window.location.href = '/login';
  }

  // Helper method to make authenticated requests
  async authenticatedFetch(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.getToken()}`
      }
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      this.handleUnauthorized();
      throw new Error('Session expired. Please login again.');
    }

    return response;
  }

  async login(username, password, totpCode = null) {
    const loginData = { username, password };
    if (totpCode) {
      loginData.totp_code = totpCode;
    }

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }

    return response.json();
  }

  async getUsers() {
    // First try the authenticated endpoint
    try {
      const response = await fetch(`${API_BASE_URL}/users/`, {
        headers: { 'Authorization': `Bearer ${this.getToken()}` }
      });

      if (response.ok) {
        return response.json();
      }
    } catch (error) {
      console.log('Authenticated endpoint failed, trying debug endpoint');
    }

    // Fallback to debug endpoint (temporary)
    const debugResponse = await fetch('http://localhost:8000/debug-users');
    if (!debugResponse.ok) {
      throw new Error('Failed to fetch users from debug endpoint');
    }

    return debugResponse.json();
  }

  async createUser(userData) {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to create user');
    }

    return response.json();
  }

  async updateUser(userId, userData) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update user');
    }

    return response.json();
  }

  async deleteUser(userId) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.getToken()}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to delete user');
    }

    return true;
  }

  async uploadCVs(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`${API_BASE_URL}/upload/cv`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.getToken()}` },
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to upload CVs');
    }

    return response.json();
  }

  async analyzeCandidates(candidateIds, jobTitle, jobRequirements) {
    const response = await fetch(`${API_BASE_URL}/analysis/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({
        candidate_ids: candidateIds,
        job_title: jobTitle,
        job_requirements: jobRequirements
      })
    });

    if (!response.ok) {
      throw new Error('Failed to analyze candidates');
    }

    return response.json();
  }

  async uploadAndAnalyzeCVs(files, jobTitle, jobRequirements) {
    console.log('uploadAndAnalyzeCVs called with:', { files: files.length, jobTitle, jobRequirements });

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('job_title', jobTitle);
    formData.append('job_requirements', jobRequirements);

    // Use demo endpoint for now (no authentication required)
    const endpoint = `${API_BASE_URL}/analysis/demo-upload-and-analyze`;
    console.log('Making request to:', endpoint);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`Failed to upload and analyze CVs: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('API Success:', result);
      return result;
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  async getCandidates() {
    const response = await fetch(`${API_BASE_URL}/candidates/`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch candidates');
    }

    return response.json();
  }

  async scheduleInterview(candidateId, datetime, type) {
    const response = await this.authenticatedFetch(`${API_BASE_URL}/interviews/schedule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        candidate_id: candidateId,
        datetime: datetime,
        type: type
      })
    });

    if (!response.ok) {
      throw new Error('Failed to schedule interview');
    }

    return response.json();
  }

  async previewInterviewEmail(candidateId, datetime, type) {
    const response = await this.authenticatedFetch(`${API_BASE_URL}/interviews/preview-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        candidate_id: candidateId,
        datetime: datetime,
        type: type
      })
    });

    if (!response.ok) {
      throw new Error('Failed to generate email preview');
    }

    return response.json();
  }

  getToken() {
    return localStorage.getItem('auth_token');
  }

  setToken(token) {
    localStorage.setItem('auth_token', token);
  }

  removeToken() {
    localStorage.removeItem('auth_token');
  }

  // 2FA Methods
  async get2FAStatus() {
    const response = await fetch(`${API_BASE_URL}/2fa/status`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      throw new Error('Failed to get 2FA status');
    }

    return response.json();
  }

  async setup2FA() {
    const response = await fetch(`${API_BASE_URL}/2fa/setup`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      throw new Error('Failed to setup 2FA');
    }

    return response.json();
  }

  async get2FAQRCode() {
    const response = await fetch(`${API_BASE_URL}/2fa/qr-code`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      throw new Error('Failed to get QR code');
    }

    return response.blob();
  }

  async verify2FA(code) {
    const response = await fetch(`${API_BASE_URL}/2fa/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ code })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to verify 2FA');
    }

    return response.json();
  }

  async disable2FA(password, code) {
    const response = await fetch(`${API_BASE_URL}/2fa/disable`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ password, code })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to disable 2FA');
    }

    return response.json();
  }

  async regenerateBackupCodes(code) {
    const response = await fetch(`${API_BASE_URL}/2fa/backup-codes/regenerate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ code })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to regenerate backup codes');
    }

    return response.json();
  }

  // Profile Management Methods
  async getProfile() {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      throw new Error('Failed to get profile');
    }

    return response.json();
  }

  async updateProfile(profileData) {
    const response = await fetch(`${API_BASE_URL}/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(profileData)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update profile');
    }

    return response.json();
  }

  async changePassword(currentPassword, newPassword) {
    const response = await fetch(`${API_BASE_URL}/profile/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to change password');
    }

    return response.json();
  }

  // Email Settings Methods
  async getEmailSettings() {
    const response = await fetch(`${API_BASE_URL}/companies/my-company/email-settings`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to get email settings');
    }

    return response.json();
  }

  async updateEmailSettings(settings) {
    const response = await fetch(`${API_BASE_URL}/companies/my-company/email-settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(settings)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update email settings');
    }

    return response.json();
  }

  async testEmailSettings(testEmail) {
    const response = await fetch(`${API_BASE_URL}/companies/my-company/email-settings/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ test_email: testEmail })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to send test email');
    }

    return response.json();
  }

  // Generic methods for flexibility
  async get(url) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Request failed');
    }

    return response.json();
  }

  async post(url, data) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Request failed');
    }

    return response.json();
  }

  async put(url, data) {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Request failed');
    }

    return response.json();
  }

  // Settings Configuration Status
  async getSettingsStatus() {
    try {
      const [twoFAStatus, emailSettings] = await Promise.all([
        this.get2FAStatus().catch(() => ({ enabled: false })),
        this.get('/companies/my-company/email-settings').catch(() => ({ smtp_enabled: false }))
      ]);

      return {
        twoFA: {
          configured: twoFAStatus.enabled || false,
          enabled: twoFAStatus.enabled || false
        },
        email: {
          configured: emailSettings.smtp_enabled || false,
          enabled: emailSettings.smtp_enabled || false
        }
      };
    } catch (error) {
      console.error('Error checking settings status:', error);
      return {
        twoFA: { configured: false, enabled: false },
        email: { configured: false, enabled: false }
      };
    }
  }
}

export default new ApiService();