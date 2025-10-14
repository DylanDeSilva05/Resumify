import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';

function Profile() {
  const [user, setUser] = useState({
    name: '',
    email: '',
    username: '',
    phone: '',
    company: '',
    position: '',
    created_at: ''
  });
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const profileData = await apiService.getProfile();

      // Load additional data from localStorage
      const additionalDataStr = localStorage.getItem('user_additional_data');
      const additionalData = additionalDataStr ? JSON.parse(additionalDataStr) : {};

      setUser({
        name: profileData.full_name || profileData.username,
        email: profileData.email,
        username: profileData.username,
        phone: additionalData.phone || '',
        company: additionalData.company || '',
        position: additionalData.position || '',
        created_at: profileData.created_at
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to load user profile:', error);
      // Fallback to demo data if API fails
      const demoUser = {
        name: 'Demo User',
        email: 'demo@resumify.com',
        username: 'demo_user',
        phone: '',
        company: '',
        position: 'Demo Mode',
        created_at: new Date().toISOString()
      };
      setUser(demoUser);
      setLoading(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const updateData = {
        full_name: user.name,
        email: user.email
      };

      const response = await apiService.updateProfile(updateData);

      // Update local state with response
      setUser({
        ...user,
        name: response.full_name || response.username,
        email: response.email,
        username: response.username
      });

      // Save phone, company, position to localStorage for now
      // (these fields aren't in the User model yet)
      const additionalData = {
        phone: user.phone,
        company: user.company,
        position: user.position
      };
      localStorage.setItem('user_additional_data', JSON.stringify(additionalData));

      setIsEditing(false);
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert(error.message || 'Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      alert('New passwords do not match!');
      return;
    }

    if (passwordForm.newPassword.length < 8) {
      alert('Password must be at least 8 characters long!');
      return;
    }

    setSaving(true);

    try {
      await apiService.changePassword(passwordForm.currentPassword, passwordForm.newPassword);
      setShowPasswordModal(false);
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      alert('Password changed successfully!');
    } catch (error) {
      console.error('Failed to change password:', error);
      alert(error.message || 'Failed to change password. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="profile-loading">
        <div className="loading-spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="bg-gradient"></div>
      <div className="grain-overlay"></div>

      <section className="profile-header">
        <div className="container">
          <h1>My Profile</h1>
          <p>Manage your account settings and preferences</p>
        </div>
      </section>

      <main className="container">
        <div className="profile-content">
          {/* Profile Card */}
          <div className="profile-card">
            <div className="profile-card-header">
              <div className="profile-avatar">
                <div className="avatar-circle">
                  {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </div>
              </div>
              <div className="profile-info">
                <h2>{user.name}</h2>
                <p className="profile-position">{user.position} at {user.company}</p>
                <p className="profile-joined">Member since {formatDate(user.created_at)}</p>
              </div>
              <div className="profile-actions">
                {!isEditing ? (
                  <button
                    className="btn-primary"
                    onClick={() => setIsEditing(true)}
                  >
                    Edit Profile
                  </button>
                ) : (
                  <div className="edit-actions">
                    <button
                      className="btn-secondary"
                      onClick={() => setIsEditing(false)}
                      disabled={saving}
                    >
                      Cancel
                    </button>
                    <button
                      className="btn-primary"
                      onClick={handleSaveProfile}
                      disabled={saving}
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Profile Form */}
            <div className="profile-form-section">
              <form onSubmit={handleSaveProfile}>
                <div className="form-grid">
                  <div className="form-group">
                    <label htmlFor="name">Full Name</label>
                    <input
                      type="text"
                      id="name"
                      value={user.name}
                      onChange={(e) => setUser(prev => ({ ...prev, name: e.target.value }))}
                      disabled={!isEditing}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="email">Email Address</label>
                    <input
                      type="email"
                      id="email"
                      value={user.email}
                      onChange={(e) => setUser(prev => ({ ...prev, email: e.target.value }))}
                      disabled={!isEditing}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                      type="text"
                      id="username"
                      value={user.username}
                      onChange={(e) => setUser(prev => ({ ...prev, username: e.target.value }))}
                      disabled={!isEditing}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="phone">Phone Number</label>
                    <input
                      type="tel"
                      id="phone"
                      value={user.phone}
                      onChange={(e) => setUser(prev => ({ ...prev, phone: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="company">Company</label>
                    <input
                      type="text"
                      id="company"
                      value={user.company}
                      onChange={(e) => setUser(prev => ({ ...prev, company: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="position">Position</label>
                    <input
                      type="text"
                      id="position"
                      value={user.position}
                      onChange={(e) => setUser(prev => ({ ...prev, position: e.target.value }))}
                      disabled={!isEditing}
                    />
                  </div>
                </div>
              </form>
            </div>
          </div>

          {/* Security Section */}
          <div className="security-card">
            <div className="card-header">
              <h3>Security Settings</h3>
              <p>Manage your account security and password</p>
            </div>
            <div className="card-content">
              <div className="security-item">
                <div className="security-info">
                  <h4>Password</h4>
                  <p>Last changed 30 days ago</p>
                </div>
                <button
                  className="btn-outline"
                  onClick={() => setShowPasswordModal(true)}
                >
                  Change Password
                </button>
              </div>

              <div className="security-item">
                <div className="security-info">
                  <h4>Two-Factor Authentication</h4>
                  <p>Add an extra layer of security to your account</p>
                </div>
                <button className="btn-outline">
                  Configure 2FA
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Password Change Modal */}
      {showPasswordModal && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowPasswordModal(false)}>
          <div className="modal-content password-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Change Password</h2>
              <span className="close" onClick={() => setShowPasswordModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <form onSubmit={handlePasswordChange}>
                <div className="form-group">
                  <label htmlFor="currentPassword">Current Password</label>
                  <input
                    type="password"
                    id="currentPassword"
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="newPassword">New Password</label>
                  <input
                    type="password"
                    id="newPassword"
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                    required
                    minLength="8"
                  />
                  <small>Password must be at least 8 characters long</small>
                </div>

                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm New Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    required
                  />
                </div>

                <div className="modal-actions">
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setShowPasswordModal(false)}
                    disabled={saving}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={saving}
                  >
                    {saving ? 'Changing...' : 'Change Password'}
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

export default Profile;