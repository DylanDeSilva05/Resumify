import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useHeaderScroll } from '../hooks/useHeaderScroll';
import { useScrollAnimations } from '../hooks/useScrollAnimations';

function Login() {
  const [loginForm, setLoginForm] = useState({ username: '', password: '', totpCode: '' });
  const [show2FA, setShow2FA] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordStep, setForgotPasswordStep] = useState(0); // ✅ IMPROVED: 0: Request OTP, 1: Verify OTP, 2: Reset Password
  const [forgotPasswordData, setForgotPasswordData] = useState({ username: '', maskedEmail: '', otp: '', newPassword: '', confirmPassword: '' });
  const [forgotPasswordError, setForgotPasswordError] = useState('');
  const [forgotPasswordSuccess, setForgotPasswordSuccess] = useState('');
  const [showDemoModal, setShowDemoModal] = useState(false);
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  // Use custom hooks
  useHeaderScroll();
  useScrollAnimations();

  const handleLogin = async (event) => {
    event.preventDefault();
    setLoginError('');

    if (!loginForm.username || !loginForm.password) {
      setLoginError('Please enter both username and password');
      return;
    }

    if (show2FA && !loginForm.totpCode) {
      setLoginError('Please enter your 2FA code');
      return;
    }

    try {
      const result = await login(
        loginForm.username,
        loginForm.password,
        show2FA ? loginForm.totpCode : null
      );

      if (result.success) {
        navigate('/dashboard');
      } else {
        // Check if 2FA is required
        if (result.requiresTwoFA) {
          setShow2FA(true);
          setLoginError('Please enter your 2FA code');
        } else {
          setLoginError(result.error || 'Login failed: Invalid credentials');
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoginError('An unexpected error occurred. Please try again.');
    }
  };

  const handleInputChange = (field, value) => {
    setLoginForm(prev => ({ ...prev, [field]: value }));
    setLoginError('');
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setForgotPasswordError('');
    setForgotPasswordSuccess('');

    // ✅ IMPROVED: Step 1 - Verify OTP (previously confusing as step "1")
    if (forgotPasswordStep === 1) {
      // Verify OTP
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/auth/verify-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: forgotPasswordData.username,
            otp: forgotPasswordData.otp
          })
        });

        const data = await response.json();

        if (response.ok) {
          setForgotPasswordSuccess('✓ OTP verified! Please set your new password.');
          setForgotPasswordStep(2);
        } else {
          setForgotPasswordError(data.detail || '❌ Invalid OTP. Please try again.');
        }
      } catch (error) {
        setForgotPasswordError('❌ Network error. Please try again.');
      }
    }
    // ✅ IMPROVED: Step 2 - Reset Password
    else if (forgotPasswordStep === 2) {
      // Reset password
      if (forgotPasswordData.newPassword !== forgotPasswordData.confirmPassword) {
        setForgotPasswordError('⚠️ Passwords do not match.');
        return;
      }

      if (forgotPasswordData.newPassword.length < 8) {
        setForgotPasswordError('⚠️ Password must be at least 8 characters long.');
        return;
      }

      // ✅ NEW VALIDATION: Check password strength
      if (!/[A-Z]/.test(forgotPasswordData.newPassword)) {
        setForgotPasswordError('⚠️ Password must contain at least one uppercase letter.');
        return;
      }

      if (!/[0-9]/.test(forgotPasswordData.newPassword)) {
        setForgotPasswordError('⚠️ Password must contain at least one number.');
        return;
      }

      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/auth/reset-password`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: forgotPasswordData.username,
            otp: forgotPasswordData.otp,
            new_password: forgotPasswordData.newPassword
          })
        });

        const data = await response.json();

        if (response.ok) {
          setForgotPasswordSuccess('✓ Password reset successful! You can now log in with your new password.');
          setTimeout(() => {
            setShowForgotPassword(false);
            setForgotPasswordStep(0);
            setForgotPasswordData({ username: '', maskedEmail: '', otp: '', newPassword: '', confirmPassword: '' });
            setForgotPasswordError('');
            setForgotPasswordSuccess('');
          }, 2000);
        } else {
          setForgotPasswordError(data.detail || '❌ Failed to reset password. Please try again.');
        }
      } catch (error) {
        setForgotPasswordError('❌ Network error. Please try again.');
      }
    }
  };

  const openForgotPasswordModal = async () => {
    // Check if username is entered
    if (!loginForm.username) {
      setLoginError('Please enter your username first to reset password');
      return;
    }

    setForgotPasswordError('');
    setForgotPasswordSuccess('');

    // Request OTP using the username from login form
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: loginForm.username })
      });

      const data = await response.json();

      if (response.ok) {
        setForgotPasswordData({
          username: loginForm.username,
          maskedEmail: data.masked_email || '',
          otp: '',
          newPassword: '',
          confirmPassword: ''
        });
        setForgotPasswordSuccess(`OTP has been sent to ${data.masked_email || 'your registered email'}`);
        setShowForgotPassword(true);
        setForgotPasswordStep(1);
      } else {
        setLoginError(data.detail || 'Failed to send OTP. Please check your username.');
      }
    } catch (error) {
      setLoginError('Network error. Please try again.');
    }
  };

  const closeForgotPasswordModal = () => {
    setShowForgotPassword(false);
    setForgotPasswordStep(1);
    setForgotPasswordData({ username: '', maskedEmail: '', otp: '', newPassword: '', confirmPassword: '' });
    setForgotPasswordError('');
    setForgotPasswordSuccess('');
  };

  return (
    <div>
      {/* Updated Header for Landing Page */}
      <header>
        <div className="header-content">
          <a href="#" className="logo">Resumify</a>
          <nav>
            <ul className="nav-links">
              <li><a href="/about">About Us</a></li>
              <li><a href="#features" onClick={() => scrollToSection('features')}>Features</a></li>
              <li><a href="#security" onClick={() => scrollToSection('security')}>Security</a></li>
              <li><a href="#contact" onClick={() => scrollToSection('contact')}>Contact</a></li>
              <li><a href="#login" onClick={() => scrollToSection('login')}>Login</a></li>
            </ul>
            <button className="mobile-menu-btn">☰</button>
          </nav>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="hero">
          <div className="hero-content">
            <div className="hero-text">
              <h1>Smart <span className="highlight">AI-Powered</span> HR Recruitment Platform</h1>
              <p>Transform your hiring process with intelligent candidate matching, automated screening, and data-driven insights. Reduce time-to-hire by 80% while finding the perfect candidates.</p>
              <div className="cta-buttons">
                <a href="#login" className="btn btn-primary" onClick={() => scrollToSection('login')}>Login →</a>
              </div>
            </div>
            <div className="hero-visual">
              <div className="dashboard-preview">
                <div className="dashboard-header1">
                  <div className="window-controls">
                    <div className="window-control control-close"></div>
                    <div className="window-control control-minimize"></div>
                    <div className="window-control control-maximize"></div>
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>HR Dashboard</span>
                </div>
                <div className="dashboard-content">
                  <div className="metric-card">
                    <span className="metric-value">247</span>
                    <span className="metric-label">CVs Processed</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">89</span>
                    <span className="metric-label">Shortlisted</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">23</span>
                    <span className="metric-label">Interviews</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Login Section */}
        <section className="login-section" id="login">
          <h3>HR Manager Access</h3>
          {loginError && (
            <div style={{
              background: '#fee',
              color: '#c33',
              padding: '12px',
              borderRadius: '8px',
              marginBottom: '20px',
              border: '1px solid #fcc'
            }}>
              {loginError}
            </div>
          )}
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                placeholder="Enter your username"
                value={loginForm.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                placeholder="Enter your password"
                value={loginForm.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                required
              />
            </div>
            {show2FA && (
              <div className="form-group">
                <label htmlFor="totpCode">2FA Code</label>
                <input
                  type="text"
                  id="totpCode"
                  name="totpCode"
                  placeholder="Enter your 6-digit 2FA code"
                  value={loginForm.totpCode}
                  onChange={(e) => handleInputChange('totpCode', e.target.value)}
                  maxLength="6"
                  pattern="[0-9]{6}"
                  style={{
                    fontFamily: 'monospace',
                    fontSize: '18px',
                    textAlign: 'center',
                    letterSpacing: '4px'
                  }}
                  required
                />
                <small style={{ color: '#666', fontSize: '12px' }}>
                  Enter the 6-digit code from your authenticator app
                </small>
              </div>
            )}
            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%' }}
              disabled={isLoading}
            >
              {isLoading ? 'Signing In...' : show2FA ? 'Verify & Login →' : 'Access Dashboard →'}
            </button>
            <div style={{ marginTop: '1rem', textAlign: 'center' }}>
              <button
                type="button"
                onClick={openForgotPasswordModal}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--primary)',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  textDecoration: 'underline'
                }}
              >
                Forgot Password?
              </button>
            </div>
          </form>
        </section>

        {/* Features Section */}
        <section className="features" id="features">
          <div className="section-header">
            <h2>Why Choose Resumify?</h2>
            <p>Powerful features designed to revolutionize your recruitment process with cutting-edge AI technology</p>
          </div>
          <div className="features-grid">
            <div className="feature-card animate-on-scroll animate-delay-1">
              <div className="feature-icon">🎯</div>
              <h3>Enhanced Accuracy</h3>
              <p>AI-powered matching ensures superior candidate-role compatibility with advanced skill assessment and cultural fit analysis.</p>
            </div>
            <div className="feature-card animate-on-scroll animate-delay-2">
              <div className="feature-icon">🧠</div>
              <h3>Smart Matching</h3>
              <p>Advanced machine learning algorithms analyze thousands of data points to find the perfect candidates for your specific requirements.</p>
            </div>
            <div className="feature-card animate-on-scroll animate-delay-3">
              <div className="feature-icon">⚖️</div>
              <h3>Bias-Free Hiring</h3>
              <p>Remove unconscious bias with objective, data-driven candidate evaluation based on skills, experience, and potential.</p>
            </div>
            <div className="feature-card animate-on-scroll animate-delay-4">
              <div className="feature-icon">📊</div>
              <h3>Analytics & Insights</h3>
              <p>Comprehensive reporting and analytics to optimize your hiring process and make informed decisions.</p>
            </div>
            <div className="feature-card animate-on-scroll animate-delay-1">
              <div className="feature-icon">🔄</div>
              <h3>Seamless Integration</h3>
              <p>Integrate with your existing HR tools and systems for a unified, streamlined workflow.</p>
            </div>
          </div>
        </section>

        {/* Security Section */}
        <section className="security-section" id="security">
          <div className="section-header">
            <h2>Enterprise-Grade Security</h2>
            <p>Your data is protected with industry-leading security measures and compliance standards</p>
          </div>
          <div className="security-features-grid">
            <div className="security-feature-item">
              <div className="security-feature-icon">🔒</div>
              <span>End-to-End Encryption</span>
            </div>
            <div className="security-feature-item">
              <div className="security-feature-icon">👥</div>
              <span>Role-Based Access Control</span>
            </div>
            <div className="security-feature-item">
              <div className="security-feature-icon">🔐</div>
              <span>Multi-Factor Authentication</span>
            </div>
            <div className="security-feature-item">
              <div className="security-feature-icon">🛡️</div>
              <span>Regular Security Audits</span>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section className="contact-section" id="contact">
          <h2>Ready to Transform Your Hiring Process?</h2>
          <p>Join thousands of companies already using Resumify to make smarter hiring decisions</p>
          <div className="contact-grid">
            <div className="contact-item">
              <div className="contact-icon">📧</div>
              <h4>Email Us</h4>
              <p>sales@resumify.com</p>
            </div>
            <div className="contact-item">
              <div className="contact-icon">📞</div>
              <h4>Call Sales</h4>
              <p>+94 (081) 123-4567</p>
            </div>
            <div className="contact-item">
              <div className="contact-icon">🎥</div>
              <h4>View Demo</h4>
              <button
                onClick={() => setShowDemoModal(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--primary)',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  fontSize: '1rem'
                }}
              >
                Watch 2-min demo
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Updated Footer for Landing Page */}
      <footer>
        <div className="footer-links">
          <a href="#features" onClick={() => scrollToSection('features')}>Features</a>
          <a href="#security" onClick={() => scrollToSection('security')}>Security</a>
          <a href="#contact" onClick={() => scrollToSection('contact')}>Contact</a>
          <a href="#login" onClick={() => scrollToSection('login')}>Login</a>
          <a href="#privacy">Privacy Policy</a>
          <a href="#terms">Terms of Service</a>
        </div>
        <p className="footer-text">&copy; 2025 Resumify. All rights reserved. | Enterprise HR Solutions</p>
      </footer>

      {/* Demo Video Modal */}
      {showDemoModal && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowDemoModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px' }}>
            <div className="modal-header">
              <h2>🎥 Resumify Platform Demo</h2>
              <span className="close" onClick={() => setShowDemoModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', background: '#000', borderRadius: '8px' }}>
                <iframe
                  src=""
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  title="Resumify Demo Video"
                />
              </div>
              <p style={{ marginTop: '1.5rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                📌 See how Resumify transforms your recruitment process in just 2 minutes
              </p>
              <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center' }}>
                Note: Replace the YouTube video ID in the code with your actual demo video
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="modal" style={{ display: 'block' }} onClick={closeForgotPasswordModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h2>Reset Password</h2>
              <span className="close" onClick={closeForgotPasswordModal}>&times;</span>
            </div>
            <div className="modal-body">
              {forgotPasswordError && (
                <div style={{
                  background: '#fee',
                  color: '#c33',
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '15px',
                  border: '1px solid #fcc'
                }}>
                  {forgotPasswordError}
                </div>
              )}
              {forgotPasswordSuccess && (
                <div style={{
                  background: '#efe',
                  color: '#3c3',
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '15px',
                  border: '1px solid #cfc'
                }}>
                  {forgotPasswordSuccess}
                </div>
              )}

              <form onSubmit={handleForgotPassword}>
                {forgotPasswordStep === 1 && (
                  <div>
                    <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                      Enter the 6-digit OTP sent to <strong>{forgotPasswordData.maskedEmail}</strong>
                    </p>
                    <div className="form-group">
                      <label htmlFor="otpCode">OTP Code</label>
                      <input
                        type="text"
                        id="otpCode"
                        placeholder="Enter 6-digit OTP"
                        value={forgotPasswordData.otp}
                        onChange={(e) => setForgotPasswordData(prev => ({ ...prev, otp: e.target.value }))}
                        maxLength="6"
                        pattern="[0-9]{6}"
                        required
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          borderRadius: '8px',
                          border: '1px solid var(--border)',
                          fontFamily: 'monospace',
                          fontSize: '18px',
                          textAlign: 'center',
                          letterSpacing: '4px'
                        }}
                      />
                    </div>
                  </div>
                )}

                {forgotPasswordStep === 2 && (
                  <div>
                    <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                      Create a new password for your account.
                    </p>
                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                      <label htmlFor="newPassword">New Password</label>
                      <input
                        type="password"
                        id="newPassword"
                        placeholder="Enter new password (min. 8 characters)"
                        value={forgotPasswordData.newPassword}
                        onChange={(e) => setForgotPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                        minLength="8"
                        required
                        style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)' }}
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="confirmPassword">Confirm Password</label>
                      <input
                        type="password"
                        id="confirmPassword"
                        placeholder="Confirm new password"
                        value={forgotPasswordData.confirmPassword}
                        onChange={(e) => setForgotPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                        minLength="8"
                        required
                        style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)' }}
                      />
                    </div>
                  </div>
                )}

                <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                  <button
                    type="button"
                    onClick={closeForgotPasswordModal}
                    style={{
                      flex: 1,
                      padding: '0.75rem',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      background: 'transparent',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    style={{ flex: 1, padding: '0.75rem' }}
                  >
                    {forgotPasswordStep === 1 ? 'Verify OTP' : 'Reset Password'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Login;
