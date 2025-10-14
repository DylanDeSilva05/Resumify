import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import ConfirmDialog from './ConfirmDialog';

function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout: authLogout } = useAuth();
  const { showToast } = useToast();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  // Public pages that don't need authentication (don't show header)
  const publicPages = ['/login', '/about'];
  if (publicPages.includes(location.pathname)) {
    return null;
  }

  // If user is not authenticated and tries to access a protected page, don't show header
  // (they'll be redirected by ProtectedRoute anyway)
  if (!isAuthenticated) {
    return null;
  }

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true);
  };

  const confirmLogout = () => {
    authLogout();
    setShowLogoutConfirm(false);
    showToast('✓ Successfully logged out. See you next time!', 'success');
    // Add delay to let user see the toast
    setTimeout(() => navigate('/login'), 2000);
  };

  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };

  const closeUserMenu = () => {
    setShowUserMenu(false);
  };

  const toggleMobileMenu = () => {
    setShowMobileMenu(!showMobileMenu);
  };

  const closeMobileMenu = () => {
    setShowMobileMenu(false);
  };

  return (
    <header>
      <div className="header-content">
        <Link to="/" className="logo">Resumify</Link>

        {/* Navigation */}
        <nav>
          <ul className={`nav-links ${showMobileMenu ? 'mobile-active' : ''}`}>
            <li><Link to="/" className={isActive('/')} onClick={closeMobileMenu}>Dashboard</Link></li>
            <li><Link to="/management" className={isActive('/management')} onClick={closeMobileMenu}>Account Management</Link></li>
            <li><Link to="/calendar" className={isActive('/calendar')} onClick={closeMobileMenu}>Calendar</Link></li>
            <li><Link to="/company" className={isActive('/company')} onClick={closeMobileMenu}>Company Profile</Link></li>
          </ul>
          <button className="mobile-menu-btn" onClick={toggleMobileMenu} aria-label="Toggle menu">
            {showMobileMenu ? '✕' : '☰'}
          </button>
        </nav>

        {/* User Menu */}
        <div className="user-menu-container">
          <button className="user-menu-btn" onClick={toggleUserMenu}>
            <div className="user-avatar">
              {(user?.user?.full_name || user?.user?.username || 'U').charAt(0).toUpperCase()}
            </div>
            <span className="user-name">
              {user?.user?.full_name || user?.user?.username || 'User'}
            </span>
            <span className="dropdown-arrow">▼</span>
          </button>

          {showUserMenu && (
            <div className="user-dropdown">
              <div className="dropdown-overlay" onClick={closeUserMenu}></div>
              <div className="dropdown-menu">
                <div className="dropdown-header">
                  <div className="user-info-dropdown">
                    <strong>{user?.user?.full_name || user?.user?.username || 'User'}</strong>
                    <small>{user?.user?.email || 'user@example.com'}</small>
                  </div>
                </div>

                <div className="dropdown-divider"></div>

                <Link
                  to="/profile"
                  className="dropdown-item"
                  onClick={closeUserMenu}
                >
                  <span>👤</span> My Profile
                </Link>

                <Link
                  to="/2fa-setup"
                  className="dropdown-item"
                  onClick={closeUserMenu}
                >
                  <span>🔐</span> Security Settings
                </Link>

                <Link
                  to="/email-settings"
                  className="dropdown-item"
                  onClick={closeUserMenu}
                >
                  <span>📧</span> Email Settings
                </Link>

                <div className="dropdown-divider"></div>

                <button
                  className="dropdown-item logout-item"
                  onClick={() => { closeUserMenu(); handleLogoutClick(); }}
                >
                  <span>🚪</span> Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <ConfirmDialog
        show={showLogoutConfirm}
        title="Ready to leave?"
        message="You're about to log out. Don't worry, your data is safe and you can come back anytime!"
        onConfirm={confirmLogout}
        onCancel={cancelLogout}
        confirmText="Yes, Log Out"
        cancelText="Stay Logged In"
        type="info"
      />
    </header>
  );
}

export default Header;