import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';
import { useToast } from '../contexts/ToastContext';

function EmailSettings() {
  const { showToast } = useToast();
  const [settings, setSettings] = useState({
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_from_name: '',
    smtp_enabled: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [testing, setTesting] = useState(false);
  const [passwordConfigured, setPasswordConfigured] = useState(false);
  const [provider, setProvider] = useState('gmail'); // 'gmail' or 'outlook'

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    // Auto-detect provider based on existing settings
    if (settings.smtp_host === 'smtp.gmail.com') {
      setProvider('gmail');
    } else if (settings.smtp_host === 'smtp.office365.com') {
      setProvider('outlook');
    }
  }, [settings.smtp_host]);

  const loadSettings = async () => {
    try {
      const response = await apiService.get('/companies/my-company/email-settings');
      setSettings({
        smtp_host: response.smtp_host || '',
        smtp_port: response.smtp_port || 587,
        smtp_username: response.smtp_username || '',
        smtp_password: '', // Never show password
        smtp_from_name: response.smtp_from_name || '',
        smtp_enabled: response.smtp_enabled || false
      });
      setPasswordConfigured(response.password_configured);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load email settings:', error);

      // If settings don't exist (404), that's okay - just use defaults
      if (error.response?.status === 404) {
        console.log('No email settings found for this company, using defaults');
        // Keep default settings from initial state
        setLoading(false);
      } else {
        // Only show error for actual failures (not 404)
        showToast('Failed to load email settings', 'error');
        setLoading(false);
      }
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const updateData = { ...settings };

      // ✅ VALIDATION: If password is being updated, validate it
      if (updateData.smtp_password && updateData.smtp_password.trim()) {
        // Gmail App Password should be 16 characters (no spaces)
        const cleanPassword = updateData.smtp_password.replace(/\s/g, '');

        if (provider === 'gmail' && cleanPassword.length !== 16) {
          showToast('⚠️ Gmail App Password must be exactly 16 characters', 'error');
          setSaving(false);
          return;
        }

        // Use cleaned password (no spaces)
        updateData.smtp_password = cleanPassword;
      } else {
        // Only send password if it was changed
        delete updateData.smtp_password;
      }

      // ✅ VALIDATION: Ensure SMTP host and port are provided
      if (!updateData.smtp_host || !updateData.smtp_port) {
        showToast('⚠️ Please fill in SMTP host and port', 'error');
        setSaving(false);
        return;
      }

      // ✅ VALIDATION: Ensure username is provided
      if (!updateData.smtp_username) {
        showToast('⚠️ Please enter your email address', 'error');
        setSaving(false);
        return;
      }

      await apiService.put('/companies/my-company/email-settings', updateData);
      showToast('✓ Email settings saved successfully!', 'success');
      setPasswordConfigured(true);

      // Clear password field after successful save
      setSettings(prev => ({ ...prev, smtp_password: '' }));
    } catch (error) {
      console.error('Failed to save email settings:', error);
      showToast(error.response?.data?.detail || 'Failed to save email settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    if (!testEmail) {
      showToast('Please enter a test email address', 'warning');
      return;
    }

    setTesting(true);
    try {
      const response = await apiService.post('/companies/my-company/email-settings/test', {
        test_email: testEmail
      });

      if (response.success) {
        showToast(response.message, 'success');
      } else {
        showToast(response.message, 'error');
      }
    } catch (error) {
      console.error('Test email failed:', error);
      showToast(error.response?.data?.detail || 'Failed to send test email', 'error');
    } finally {
      setTesting(false);
    }
  };

  const handleProviderChange = (selectedProvider) => {
    console.log('Provider changed to:', selectedProvider);
    setProvider(selectedProvider);

    // Auto-fill settings based on provider
    if (selectedProvider === 'gmail') {
      console.log('Setting Gmail SMTP settings');
      setSettings(prev => ({
        ...prev,
        smtp_host: 'smtp.gmail.com',
        smtp_port: 587
      }));
      showToast('Gmail settings applied! Now enter your email and App Password below.', 'success');
    } else if (selectedProvider === 'outlook') {
      console.log('Setting Outlook SMTP settings');
      setSettings(prev => ({
        ...prev,
        smtp_host: 'smtp.office365.com',
        smtp_port: 587
      }));
      showToast('Outlook settings applied! Now enter your email and password below.', 'success');
    }
  };

  const openGoogleAppPassword = () => {
    window.open('https://myaccount.google.com/apppasswords', '_blank');
    showToast('Opening Google App Passwords. Generate a password and paste it below!', 'info');
  };

  if (loading) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="loading-spinner-large"></div>
          <p>Loading email settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <section className="page-header">
        <div className="container">
          <h1>📧 Email Settings</h1>
          <p>Configure SMTP settings for sending interview invitations and notifications</p>
        </div>
      </section>

      <main className="container">
        <div className="email-settings-content">
          {/* Quick Setup Card */}
          <div className="info-card">
            <h3>⚡ Quick Email Setup</h3>
            <p style={{ marginBottom: '1.5rem' }}>Choose your email provider and we'll guide you through the setup:</p>

            {/* Provider Selection */}
            <div className="provider-selection">
              <button
                className={`provider-btn ${provider === 'gmail' ? 'active' : ''}`}
                onClick={() => handleProviderChange('gmail')}
              >
                <span className="provider-icon">📧</span>
                <strong>Gmail</strong>
                <small>Recommended</small>
              </button>
              <button
                className={`provider-btn ${provider === 'outlook' ? 'active' : ''}`}
                onClick={() => handleProviderChange('outlook')}
              >
                <span className="provider-icon">📨</span>
                <strong>Outlook</strong>
                <small>Office 365</small>
              </button>
            </div>

            {/* Gmail Instructions */}
            {provider === 'gmail' && (
              <div className="setup-steps">
                <h4>📝 Setup Steps for Gmail:</h4>
                <div className="step-card">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <strong>Get your App Password from Google</strong>
                    <p>Click the button below to open Google's App Password page:</p>
                    <button className="quick-action-btn" onClick={openGoogleAppPassword}>
                      🔗 Open Google App Passwords
                    </button>
                    <small style={{ display: 'block', marginTop: '0.5rem' }}>
                      💡 In the Google page: Select "Mail" → "Other" → Type "Resumify" → Generate
                    </small>
                  </div>
                </div>

                <div className="step-card">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <strong>Fill in the form below</strong>
                    <p>The SMTP settings are already filled! Just add your email and the App Password.</p>
                  </div>
                </div>

                <div className="step-card">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <strong>Save and Test</strong>
                    <p>Click "Save Settings" then send a test email to verify it works!</p>
                  </div>
                </div>
              </div>
            )}

            {/* Outlook Instructions */}
            {provider === 'outlook' && (
              <div className="setup-steps">
                <h4>📝 Setup Steps for Outlook:</h4>
                <div className="step-card">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <strong>Use your Outlook credentials</strong>
                    <p>The SMTP settings are already filled! Just enter your Outlook email and password below.</p>
                  </div>
                </div>

                <div className="step-card">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <strong>Save and Test</strong>
                    <p>Click "Save Settings" then send a test email to verify it works!</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Settings Form */}
          <form onSubmit={handleSave} className="settings-form">
            <h2>SMTP Configuration</h2>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="smtp_host">📧 SMTP Host * {settings.smtp_host && '✓'}</label>
                <input
                  type="text"
                  id="smtp_host"
                  value={settings.smtp_host}
                  onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
                  placeholder="smtp.gmail.com"
                  required
                  style={{
                    background: settings.smtp_host ? 'rgba(74, 222, 128, 0.1)' : 'var(--bg-primary)',
                    borderColor: settings.smtp_host ? '#4ade80' : 'var(--border)'
                  }}
                />
                <small style={{ color: settings.smtp_host ? '#4ade80' : 'var(--text-muted)' }}>
                  {settings.smtp_host ? `✓ Using ${settings.smtp_host}` : 'Select a provider above to auto-fill'}
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="smtp_port">🔌 SMTP Port * {settings.smtp_port && '✓'}</label>
                <input
                  type="number"
                  id="smtp_port"
                  value={settings.smtp_port}
                  onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })}
                  required
                  min="1"
                  max="65535"
                  placeholder="587"
                  style={{
                    background: settings.smtp_port ? 'rgba(74, 222, 128, 0.1)' : 'var(--bg-primary)',
                    borderColor: settings.smtp_port ? '#4ade80' : 'var(--border)'
                  }}
                />
                <small style={{ color: settings.smtp_port ? '#4ade80' : 'var(--text-muted)' }}>
                  {settings.smtp_port ? `✓ Using port ${settings.smtp_port}` : 'Select a provider above to auto-fill'}
                </small>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="smtp_username">👤 Your Email Address *</label>
              <input
                type="email"
                id="smtp_username"
                value={settings.smtp_username}
                onChange={(e) => setSettings({ ...settings, smtp_username: e.target.value })}
                placeholder="yourname@gmail.com"
                required
              />
              <small>The email address you want to send from</small>
            </div>

            <div className="form-group">
              <label htmlFor="smtp_password">🔑 App Password {passwordConfigured && '✓ Saved'} *</label>
              <input
                type="password"
                id="smtp_password"
                value={settings.smtp_password}
                onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
                placeholder={passwordConfigured ? "Leave blank to keep current" : "Paste your 16-character App Password here"}
                required={!passwordConfigured}
              />
              <small style={{ color: passwordConfigured ? '#4ade80' : 'var(--text-muted)' }}>
                {passwordConfigured ? '✓ Password is saved securely' : '⚠️ NOT your Gmail password - use the App Password from Google'}
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="smtp_from_name">🏢 Display Name (Optional)</label>
              <input
                type="text"
                id="smtp_from_name"
                value={settings.smtp_from_name}
                onChange={(e) => setSettings({ ...settings, smtp_from_name: e.target.value })}
                placeholder="ABC Company HR Team"
              />
              <small>This name will appear in emails sent to candidates</small>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={settings.smtp_enabled}
                  onChange={(e) => setSettings({ ...settings, smtp_enabled: e.target.checked })}
                />
                <span>✅ Enable Email Sending</span>
              </label>
              <small>Check this box to activate automatic email sending for interview invitations</small>
            </div>

            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? '⏳ Saving Settings...' : '💾 Save Settings'}
            </button>
          </form>

          {/* Test Email Section */}
          {passwordConfigured && (
            <div className="test-email-section">
              <h2>🧪 Step 3: Test Your Configuration</h2>
              <p>Send a test email to verify everything is working correctly. Enter any email address (it can be your own email to check).</p>

              <div className="test-email-form">
                <input
                  type="email"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                  placeholder="Enter your email to receive a test message"
                  className="test-email-input"
                />
                <button
                  onClick={handleTest}
                  disabled={testing || !testEmail || !settings.smtp_enabled}
                  className="btn-secondary"
                >
                  {testing ? '📤 Sending...' : '📨 Send Test Email'}
                </button>
              </div>
              {!settings.smtp_enabled && (
                <small style={{ color: '#f59e0b', display: 'block', marginTop: '0.5rem' }}>
                  ⚠️ Please enable email sending above before testing
                </small>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default EmailSettings;
