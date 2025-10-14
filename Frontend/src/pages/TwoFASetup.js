import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';

function TwoFASetup() {
  const [currentStep, setCurrentStep] = useState('status'); // status, setup, verify, complete
  const [twoFAStatus, setTwoFAStatus] = useState(null);
  const [setupData, setSetupData] = useState(null);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadTwoFAStatus();
  }, []);

  const loadTwoFAStatus = async () => {
    try {
      const status = await apiService.get2FAStatus();
      setTwoFAStatus(status);
    } catch (error) {
      setError('Failed to load 2FA status');
      console.error('Error loading 2FA status:', error);
    }
  };

  const startSetup = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await apiService.setup2FA();
      setSetupData(response);

      // Get QR code
      const qrBlob = await apiService.get2FAQRCode();
      const qrUrl = URL.createObjectURL(qrBlob);
      setQrCodeUrl(qrUrl);

      setCurrentStep('setup');
    } catch (error) {
      setError(error.message || 'Failed to setup 2FA');
    } finally {
      setIsLoading(false);
    }
  };

  const verifySetup = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await apiService.verify2FA(verificationCode);
      setBackupCodes(response.backup_codes);
      setSuccess('2FA has been successfully enabled!');
      setCurrentStep('complete');
      await loadTwoFAStatus();
    } catch (error) {
      setError(error.message || 'Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const disable2FA = async () => {
    const password = prompt('Enter your password to disable 2FA:');
    const code = prompt('Enter your current 2FA code:');

    if (!password || !code) return;

    setIsLoading(true);
    setError('');

    try {
      await apiService.disable2FA(password, code);
      setSuccess('2FA has been disabled');
      setCurrentStep('status');
      await loadTwoFAStatus();
    } catch (error) {
      setError(error.message || 'Failed to disable 2FA');
    } finally {
      setIsLoading(false);
    }
  };

  const regenerateBackupCodes = async () => {
    const code = prompt('Enter your current 2FA code to regenerate backup codes:');
    if (!code) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await apiService.regenerateBackupCodes(code);
      setBackupCodes(response.backup_codes);
      setSuccess('New backup codes generated successfully!');
    } catch (error) {
      setError(error.message || 'Failed to regenerate backup codes');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    const codesText = backupCodes.join('\n');
    const blob = new Blob([codesText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resumify-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <section className="page-header">
        <div className="container">
          <button
            onClick={() => navigate('/dashboard')}
            className="back-btn"
            style={{
              marginBottom: '1rem',
              padding: '0.5rem 1rem',
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              cursor: 'pointer',
              color: 'var(--text-primary)'
            }}
          >
            ← Back to Dashboard
          </button>
          <h1>Two-Factor Authentication</h1>
          <p>Enhance your account security with two-factor authentication</p>
        </div>
      </section>

      <main className="container">
        <div className="twofa-content"
             style={{
               maxWidth: '600px',
               margin: '0 auto',
               background: 'var(--surface)',
               padding: '2rem',
               borderRadius: '20px',
               border: '1px solid var(--border)'
             }}>

          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--danger)',
              padding: '12px',
              borderRadius: '8px',
              marginBottom: '20px',
              border: '1px solid var(--danger)'
            }}>
              {error}
            </div>
          )}

          {success && (
            <div style={{
              background: 'rgba(16, 185, 129, 0.1)',
              color: 'var(--success)',
              padding: '12px',
              borderRadius: '8px',
              marginBottom: '20px',
              border: '1px solid var(--success)'
            }}>
              {success}
            </div>
          )}

      {/* Status Step */}
      {currentStep === 'status' && twoFAStatus && (
        <div>
          <h3>Current Status</h3>
          <p>
            <strong>2FA Status:</strong> {twoFAStatus.enabled ? '✅ Enabled' : '❌ Disabled'}
          </p>
          {twoFAStatus.enabled && (
            <p>
              <strong>Backup Codes Remaining:</strong> {twoFAStatus.backup_codes_remaining}
            </p>
          )}

          <div style={{ marginTop: '20px' }}>
            {!twoFAStatus.enabled ? (
              <button
                onClick={startSetup}
                disabled={isLoading}
                style={{
                  padding: '12px 24px',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginRight: '10px'
                }}
              >
                {isLoading ? 'Setting up...' : 'Enable 2FA'}
              </button>
            ) : (
              <div>
                <button
                  onClick={disable2FA}
                  disabled={isLoading}
                  style={{
                    padding: '12px 24px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginRight: '10px'
                  }}
                >
                  {isLoading ? 'Disabling...' : 'Disable 2FA'}
                </button>
                <button
                  onClick={regenerateBackupCodes}
                  disabled={isLoading}
                  style={{
                    padding: '12px 24px',
                    background: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {isLoading ? 'Regenerating...' : 'Regenerate Backup Codes'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Setup Step */}
      {currentStep === 'setup' && (
        <div>
          <h3>Setup Two-Factor Authentication</h3>
          <p>Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)</p>

          {qrCodeUrl && (
            <div style={{ textAlign: 'center', margin: '20px 0' }}>
              <img
                src={qrCodeUrl}
                alt="2FA QR Code"
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '10px',
                  background: 'white'
                }}
              />
            </div>
          )}

          {setupData && (
            <div style={{
              background: '#f8f9fa',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <p style={{ color: '#212529' }}><strong>Manual Entry Key:</strong></p>
              <code style={{
                background: '#e9ecef',
                padding: '8px',
                borderRadius: '4px',
                display: 'block',
                wordBreak: 'break-all',
                fontFamily: 'monospace',
                color: '#212529'
              }}>
                {setupData.manual_entry_key}
              </code>
            </div>
          )}

          <div>
            <label htmlFor="verificationCode">Enter verification code from your app:</label>
            <input
              type="text"
              id="verificationCode"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              maxLength="6"
              placeholder="123456"
              style={{
                width: '150px',
                padding: '10px',
                fontSize: '18px',
                textAlign: 'center',
                letterSpacing: '4px',
                fontFamily: 'monospace',
                margin: '10px 0',
                display: 'block'
              }}
            />
            <button
              onClick={verifySetup}
              disabled={isLoading || verificationCode.length !== 6}
              style={{
                padding: '12px 24px',
                background: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {isLoading ? 'Verifying...' : 'Verify & Enable 2FA'}
            </button>
          </div>
        </div>
      )}

      {/* Complete Step */}
      {currentStep === 'complete' && (
        <div>
          <h3>🎉 2FA Setup Complete!</h3>
          <p>Your account is now protected with two-factor authentication.</p>

          {backupCodes.length > 0 && (
            <div style={{
              background: '#fff3cd',
              border: '1px solid #ffeaa7',
              borderRadius: '8px',
              padding: '20px',
              marginTop: '20px'
            }}>
              <h4>⚠️ Important: Save Your Backup Codes</h4>
              <p>These backup codes can be used to access your account if you lose your authenticator device. Save them in a secure location!</p>

              <div style={{
                background: 'white',
                padding: '15px',
                borderRadius: '4px',
                margin: '10px 0',
                fontFamily: 'monospace',
                fontSize: '14px',
                color: '#212529'
              }}>
                {backupCodes.map((code, index) => (
                  <div key={index} style={{ color: '#212529' }}>{code}</div>
                ))}
              </div>

              <button
                onClick={downloadBackupCodes}
                style={{
                  padding: '8px 16px',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginRight: '10px'
                }}
              >
                Download Codes
              </button>

              <button
                onClick={() => setCurrentStep('status')}
                style={{
                  padding: '8px 16px',
                  background: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Continue
              </button>
            </div>
          )}
        </div>
      )}

      {/* Backup codes display */}
      {backupCodes.length > 0 && currentStep === 'status' && (
        <div style={{
          background: '#f8f9fa',
          padding: '15px',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <h4 style={{ color: '#212529' }}>Your Latest Backup Codes:</h4>
          <div style={{
            background: 'white',
            padding: '15px',
            borderRadius: '4px',
            margin: '10px 0',
            fontFamily: 'monospace',
            fontSize: '14px',
            color: '#212529'
          }}>
            {backupCodes.map((code, index) => (
              <div key={index} style={{ color: '#212529' }}>{code}</div>
            ))}
          </div>
          <button
            onClick={downloadBackupCodes}
            style={{
              padding: '8px 16px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Download Codes
          </button>
        </div>
      )}
        </div>
      </main>
    </div>
  );
}

export default TwoFASetup;