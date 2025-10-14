import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';
import { useHeaderScroll } from '../hooks/useHeaderScroll';
import { useScrollAnimations } from '../hooks/useScrollAnimations';
import { useToast } from '../contexts/ToastContext';
import ConfirmDialog from '../components/ConfirmDialog';

function Management() {
  const { showToast } = useToast();
  const [hrTeamMembers, setHrTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authToken, setAuthToken] = useState(null);

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    title: '',
    message: '',
    type: 'warning',
    onConfirm: null
  });

  // Edit user modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [editForm, setEditForm] = useState({
    full_name: '',
    email: '',
    role: ''
  });

  // ✅ Use custom hooks instead of setupScrollEffects
  useHeaderScroll();
  useScrollAnimations();

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      // Use existing token if available
      const existingToken = apiService.getToken();
      console.log('Current token from storage:', existingToken);

      if (existingToken && existingToken !== 'demo-token') {
        setAuthToken(existingToken);
        console.log('Using existing auth token, attempting to load real users...');
        await loadTeamMembers();
      } else {
        console.log('No valid auth token found, using demo mode');
        setAuthToken('demo-token');
        await loadTeamMembers();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuthToken('demo-token');
      await loadTeamMembers();
    }
  };

  const setupScrollEffects = () => {
    const handleScroll = () => {
      const header = document.querySelector('header');
      if (header) {
        const currentScrollY = window.scrollY;
        if (currentScrollY > 100) {
          header.style.background = 'rgba(15, 23, 42, 0.95)';
        } else {
          header.style.background = 'rgba(15, 23, 42, 0.8)';
        }
      }
    };

    // Scroll-triggered animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.animationPlayState = 'running';
        }
      });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      el.style.animationPlayState = 'paused';
      observer.observe(el);
    });

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  };

  const loadTeamMembers = async () => {
    setLoading(true);
    try {
      // Always try to fetch real users from API first
      const response = await apiService.getUsers();
      console.log('API Response:', response);

      // Handle different response formats
      if (Array.isArray(response)) {
        setHrTeamMembers(response);
      } else if (response.users && Array.isArray(response.users)) {
        setHrTeamMembers(response.users);
      } else if (response.data && Array.isArray(response.data)) {
        setHrTeamMembers(response.data);
      } else {
        console.log('Unexpected response format:', response);
        setHrTeamMembers([]);
      }
    } catch (err) {
      console.error('Failed to load team members:', err);

      // Only show demo data if specifically in demo mode
      if (authToken === 'demo-token') {
        setHrTeamMembers([
          {
            id: 1,
            username: "hr_manager",
            email: "hr.manager@techcorp.com",
            full_name: "John Smith",
            user_type: "hr_manager",
            is_active: true,
          },
          {
            id: 2,
            username: "hr_team",
            email: "hr.team@techcorp.com",
            full_name: "Sarah Johnson",
            user_type: "hr_team",
            is_active: true,
          },
        ]);
      } else {
        // Show empty state for real API errors
        setHrTeamMembers([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const createUser = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const userData = {
      username: formData.get("username"),
      email: formData.get("email"),
      full_name: formData.get("full_name"),
      password: formData.get("password"),
      role: formData.get("role") || "company_user",  // Updated to use 'role'
      is_active: true
    };

    const submitBtn = event.target.querySelector('.create-btn');
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = 'Creating...';
    submitBtn.disabled = true;

    try {
      if (authToken === 'demo-token') {
        // Demo mode simulation
        await new Promise(resolve => setTimeout(resolve, 1000));
        showToast(`Demo: HR team member "${userData.full_name}" created successfully!`, 'success');
      } else {
        await apiService.createUser(userData);
        showToast(`HR team member "${userData.full_name}" created successfully!`, 'success');
      }

      event.target.reset();
      await loadTeamMembers();
    } catch (err) {
      console.error('Create user error:', err);
      showToast(`Failed to create user: ${err.message || 'Unknown error'}`, 'error');
    } finally {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    }
  };

  const getRoleName = (roleOrType) => {
    // Unified role map
    const roleMap = {
      // New unified roles
      "super_admin": "🔑 Super Admin",
      "SUPER_ADMIN": "🔑 Super Admin",
      "company_admin": "👔 Company Admin",
      "COMPANY_ADMIN": "👔 Company Admin",
      "company_user": "👤 Company User",
      "COMPANY_USER": "👤 Company User",
      "recruiter": "🎯 Recruiter",
      "RECRUITER": "🎯 Recruiter",

      // Old types for backward compatibility (will be migrated)
      "admin_hr": "👔 Company Admin",
      "ADMIN_HR": "👔 Company Admin",
      "standard_hr": "👤 Company User",
      "STANDARD_HR": "👤 Company User",
      "recruiter_hr": "🎯 Recruiter",
      "RECRUITER_HR": "🎯 Recruiter",
      "hr_manager": "👔 HR Manager",
      "hr_team": "👤 HR Team Member"
    };

    // Clean enum format like "UserType.ADMIN_HR" or "UserRole.COMPANY_ADMIN"
    const cleanValue = typeof roleOrType === 'string'
      ? roleOrType.replace('UserType.', '').replace('UserRole.', '')
      : roleOrType;

    return roleMap[cleanValue] || cleanValue;
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setEditForm({
      full_name: user.full_name,
      email: user.email,
      role: user.role || user.user_type
    });
    setShowEditModal(true);
  };

  const closeEditModal = () => {
    setShowEditModal(false);
    setEditingUser(null);
    setEditForm({ full_name: '', email: '', role: '' });
  };

  const saveUserEdit = async (event) => {
    event.preventDefault();

    try {
      await apiService.updateUser(editingUser.id, {
        full_name: editForm.full_name,
        email: editForm.email,
        role: editForm.role
      });
      showToast("✓ User updated successfully!", 'success');
      closeEditModal();
      await loadTeamMembers();
    } catch (error) {
      console.error("Failed to update user:", error);
      showToast("❌ Failed to update user: " + error.message, 'error');
    }
  };

  const handleToggleUserStatus = (user) => {
    const action = user.is_active ? "deactivate" : "activate";
    setConfirmDialog({
      show: true,
      title: `${action.charAt(0).toUpperCase() + action.slice(1)} User?`,
      message: `Are you sure you want to ${action} ${user.full_name}?`,
      type: 'warning',
      onConfirm: async () => {
        setConfirmDialog({ ...confirmDialog, show: false });
        try {
          await apiService.updateUser(user.id, {
            is_active: !user.is_active
          });
          showToast(`✓ User ${action}d successfully!`, 'success');
          await loadTeamMembers();
        } catch (error) {
          console.error(`Failed to ${action} user:`, error);
          showToast(`❌ Failed to ${action} user: ` + error.message, 'error');
        }
      }
    });
  };

  const handleDeleteUser = (user) => {
    setConfirmDialog({
      show: true,
      title: 'Delete User Account?',
      message: `Are you sure you want to permanently delete ${user.full_name}? This action cannot be undone and will remove all user data.`,
      type: 'danger',
      onConfirm: async () => {
        setConfirmDialog({ ...confirmDialog, show: false });
        try {
          await apiService.deleteUser(user.id);
          showToast("✓ User deleted successfully!", 'success');
          await loadTeamMembers();
        } catch (error) {
          console.error("Failed to delete user:", error);
          showToast("❌ Failed to delete user: " + error.message, 'error');
        }
      }
    });
  };

  return (
    <div>
      <section className="page-header">
        <div className="container">
          <h1>Account Management</h1>
          <p>Create and manage user accounts with role-based access control</p>
        </div>
      </section>

      <main className="container">
        <div className="hr-content">
          {/* Create User Section */}
          <div className="create-user-section animate-on-scroll">
            <h2 className="section-title">Create New HR Member</h2>
            <form onSubmit={createUser}>
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  required
                  placeholder="johndoe"
                  pattern="[a-zA-Z0-9_]+"
                  title="Username can only contain letters, numbers, and underscores"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input type="email" id="email" name="email" required placeholder="john.doe@company.com" />
              </div>

              <div className="form-group">
                <label htmlFor="fullName">Full Name</label>
                <input type="text" id="fullName" name="full_name" required placeholder="John Doe" />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Minimum 8 characters" minLength="8" />
              </div>

              <div className="form-group">
                <label htmlFor="role">User Role</label>
                <select id="role" name="role" required>
                  <option value="">Select User Role</option>
                  <option value="company_admin">👔 Company Admin (Full Access - Can manage users)</option>
                  <option value="company_user">👤 Company User (Standard Access - Can use all features)</option>
                  <option value="recruiter">🎯 Recruiter (Limited Access - CV screening & interviews only)</option>
                </select>
                <small style={{ display: 'block', marginTop: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  💡 <strong>Note:</strong> Company Admin has full access including user management. Company User can use all features except user management.
                </small>
              </div>

              <button type="submit" className="create-btn">Create User Account</button>
            </form>
          </div>

          {/* Permissions Section */}
          <div className="permissions-section animate-on-scroll animate-delay-1">
            <h2 className="section-title">Role Permissions</h2>
            <p>All HR team members have view-only access by default. Manager maintains full control.</p>

            <div className="permissions-grid">
              {[
                { id: "viewDashboard", name: "View Dashboard", desc: "Access to main dashboard and candidate overview", checked: true },
                { id: "viewCandidates", name: "View Candidates", desc: "See candidate lists and details", checked: true },
                { id: "viewCalendar", name: "View Calendar", desc: "See scheduled interviews", checked: true },
                { id: "uploadCv", name: "Upload CVs", desc: "Manager only - Upload and manage CV files", checked: false },
                { id: "createJobs", name: "Create Job Roles", desc: "Manager only - Define job criteria and requirements", checked: false },
                { id: "manageUsers", name: "User Management", desc: "Manager only - Create and manage HR team accounts", checked: false },
              ].map((perm) => (
                <div className="permission-item" key={perm.id}>
                  <input type="checkbox" id={perm.id} className="permission-checkbox" checked={perm.checked} disabled />
                  <label htmlFor={perm.id} className="permission-label">
                    <strong>{perm.name}</strong>
                    <div className="permission-desc">{perm.desc}</div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* HR Team List */}
        <div className="hr-team-list animate-on-scroll animate-delay-2">
          <div className="team-header">
            <h2 className="section-title">HR Team Members</h2>
            <div className="team-stats">
              <div className="stat-item">
                <div className="stat-number">{hrTeamMembers.length}</div>
                <div className="stat-label">Total Members</div>
              </div>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: "center", padding: "2rem" }}>
              <div className="loading-spinner"></div>
              <p>Loading team members...</p>
            </div>
          ) : (
            <table className="team-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {hrTeamMembers.length === 0 ? (
                  <tr>
                    <td colSpan={6}>
                      <div className="empty-state">
                        <div className="icon">👥</div>
                        <p>No HR team members found.</p>
                        <p>Create your first team member using the form above.</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  hrTeamMembers.map((member) => {
                    // Check if user is a Super Admin or the current logged-in user
                    const isSuperAdmin = member.role === "SUPER_ADMIN" || member.role === "super_admin";
                    const isCurrentUser = member.id === 1; // You might want to check against actual logged-in user
                    const cannotEdit = isSuperAdmin; // Cannot edit super admins

                    return (
                    <tr key={member.id}>
                      <td style={{ fontWeight: 600 }}>{member.full_name}</td>
                      <td>{member.email}</td>
                      <td>{member.username}</td>
                      <td><span className="role-badge">{getRoleName(member.role || member.user_type)}</span></td>
                      <td>
                        <span className={`status-badge ${member.is_active ? "status-active" : "status-inactive"}`}>
                          {member.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td>
                        <div className="actions-cell">
                          <button
                            className="action-btn edit-btn"
                            disabled={cannotEdit}
                            onClick={() => handleEditUser(member)}
                            title={cannotEdit ? "Cannot edit Super Admin" : "Edit user"}
                          >
                            Edit
                          </button>
                          <button
                            className="action-btn toggle-btn"
                            disabled={cannotEdit}
                            onClick={() => handleToggleUserStatus(member)}
                            title={cannotEdit ? "Cannot modify Super Admin" : member.is_active ? "Deactivate" : "Activate"}
                          >
                            {member.is_active ? "Deactivate" : "Activate"}
                          </button>
                          <button
                            className="action-btn delete-btn"
                            disabled={cannotEdit}
                            onClick={() => handleDeleteUser(member)}
                            title={cannotEdit ? "Cannot delete Super Admin" : "Delete user"}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                  })
                )}
              </tbody>
            </table>
          )}
        </div>
      </main>

      {/* Edit User Modal */}
      {showEditModal && editingUser && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content">
            <div className="modal-header">
              <h2>Edit User</h2>
              <span className="close" onClick={closeEditModal}>&times;</span>
            </div>
            <div className="modal-body">
              <form onSubmit={saveUserEdit}>
                <div className="form-group">
                  <label htmlFor="edit-full-name">Full Name</label>
                  <input
                    type="text"
                    id="edit-full-name"
                    value={editForm.full_name}
                    onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                    required
                    placeholder="John Doe"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="edit-email">Email Address</label>
                  <input
                    type="email"
                    id="edit-email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                    required
                    placeholder="john.doe@company.com"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="edit-role">User Role</label>
                  <select
                    id="edit-role"
                    value={editForm.role}
                    onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
                    required
                  >
                    <option value="">Select User Role</option>
                    <option value="company_admin">👔 Company Admin (Full Access - Can manage users)</option>
                    <option value="company_user">👤 Company User (Standard Access - Can use all features)</option>
                    <option value="recruiter">🎯 Recruiter (Limited Access - CV screening & interviews only)</option>
                  </select>
                </div>

                <div className="modal-actions">
                  <button type="submit" className="save-btn">Save Changes</button>
                  <button type="button" className="cancel-btn" onClick={closeEditModal}>Cancel</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmDialog
        show={confirmDialog.show}
        title={confirmDialog.title}
        message={confirmDialog.message}
        type={confirmDialog.type}
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog({ ...confirmDialog, show: false })}
      />
    </div>
  );
}

export default Management;