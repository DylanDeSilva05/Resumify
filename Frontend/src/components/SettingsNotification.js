import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';

function SettingsNotification() {
  const [settingsStatus, setSettingsStatus] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkSettings();

    // Check if user has dismissed the notification in this session
    const isDismissed = sessionStorage.getItem('settings_notification_dismissed');
    if (isDismissed === 'true') {
      setDismissed(true);
    }
  }, []);

  const checkSettings = async () => {
    try {
      const status = await apiService.getSettingsStatus();
      setSettingsStatus(status);
    } catch (error) {
      console.error('Error checking settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    sessionStorage.setItem('settings_notification_dismissed', 'true');
  };

  const navigateToSettings = (type) => {
    if (type === 'security') {
      navigate('/2fa-setup');
    } else if (type === 'email') {
      navigate('/email-settings');
    }
  };

  if (loading || dismissed || !settingsStatus) {
    return null;
  }

  const needsConfiguration = !settingsStatus.twoFA.configured || !settingsStatus.email.configured;

  if (!needsConfiguration) {
    return null;
  }

  return (
    <div style={{
      position: 'relative',
      background: 'linear-gradient(135deg, #fef3c7, #fde68a)',
      border: '1px solid #f59e0b',
      borderRadius: '12px',
      padding: '1.25rem',
      marginBottom: '1.5rem',
      boxShadow: '0 4px 12px rgba(245, 158, 11, 0.2)'
    }}>
      {/* Close button */}
      <button
        onClick={handleDismiss}
        style={{
          position: 'absolute',
          top: '0.75rem',
          right: '0.75rem',
          background: 'transparent',
          border: 'none',
          color: '#92400e',
          fontSize: '1.5rem',
          cursor: 'pointer',
          padding: '0.25rem',
          lineHeight: 1,
          transition: 'all 0.2s ease'
        }}
        onMouseOver={(e) => {
          e.target.style.transform = 'scale(1.1)';
          e.target.style.color = '#78350f';
        }}
        onMouseOut={(e) => {
          e.target.style.transform = 'scale(1)';
          e.target.style.color = '#92400e';
        }}
      >
        ×
      </button>

      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{
          fontSize: '2rem',
          flexShrink: 0
        }}>
          ⚠️
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{
            margin: '0 0 0.75rem 0',
            fontSize: '1.1rem',
            fontWeight: '700',
            color: '#92400e'
          }}>
            Action Required: Configure Your Settings
          </h3>
          <p style={{
            margin: '0 0 1rem 0',
            fontSize: '0.95rem',
            color: '#78350f',
            lineHeight: '1.5'
          }}>
            To ensure optimal security and functionality, please configure the following settings:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
            {!settingsStatus.twoFA.configured && (
              <div style={{
                background: 'rgba(255, 255, 255, 0.6)',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '1.25rem' }}>🔐</span>
                  <div>
                    <strong style={{ color: '#92400e', fontSize: '0.95rem' }}>Two-Factor Authentication</strong>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#78350f' }}>
                      Enhance account security with 2FA
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => navigateToSettings('security')}
                  style={{
                    padding: '0.5rem 1rem',
                    background: '#f59e0b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = '#d97706';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = '#f59e0b';
                    e.target.style.transform = 'translateY(0)';
                  }}
                >
                  Configure 2FA
                </button>
              </div>
            )}

            {!settingsStatus.email.configured && (
              <div style={{
                background: 'rgba(255, 255, 255, 0.6)',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '1.25rem' }}>📧</span>
                  <div>
                    <strong style={{ color: '#92400e', fontSize: '0.95rem' }}>Email Settings</strong>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#78350f' }}>
                      Configure SMTP to send interview invitations
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => navigateToSettings('email')}
                  style={{
                    padding: '0.5rem 1rem',
                    background: '#f59e0b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.background = '#d97706';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.background = '#f59e0b';
                    e.target.style.transform = 'translateY(0)';
                  }}
                >
                  Configure Email
                </button>
              </div>
            )}
          </div>

          <p style={{
            margin: 0,
            fontSize: '0.8rem',
            color: '#92400e',
            fontStyle: 'italic'
          }}>
            💡 You can dismiss this notification, but it will reappear on your next login until settings are configured.
          </p>
        </div>
      </div>
    </div>
  );
}

export default SettingsNotification;
