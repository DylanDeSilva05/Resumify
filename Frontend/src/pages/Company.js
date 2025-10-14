import React, { useState, useEffect } from 'react';
import { useToast } from '../contexts/ToastContext';
import ConfirmDialog from '../components/ConfirmDialog';

function Company() {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('basic');
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState('🏢');

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    title: '',
    message: '',
    type: 'warning',
    onConfirm: null
  });

  // Company data state
  const [companyData, setCompanyData] = useState({
    id: null,
    company_name: 'Your Company',
    contact_email: '',
    contact_phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    is_active: true,
    subscription_tier: 'basic',
    max_users: 5,
    max_cv_uploads_monthly: 100,
    // Legacy fields for backward compatibility
    name: 'Your Company',
    industry: 'Not set',
    founded: '',
    size: '',
    headquarters: '',
    timezone: '',
    description: '',
    mainPhone: '',
    hrPhone: '',
    mainEmail: '',
    hrEmail: '',
    website: '',
    linkedin: '',
    careersPage: ''
  });

  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState(null);

  const [departments, setDepartments] = useState([
    { id: 1, name: 'Engineering', employees: 45, description: 'Software development and technical operations' },
    { id: 2, name: 'Product Management', employees: 12, description: 'Product strategy and roadmap planning' },
    { id: 3, name: 'Sales & Marketing', employees: 18, description: 'Business development and customer acquisition' },
    { id: 4, name: 'Human Resources', employees: 8, description: 'Talent acquisition and employee relations' },
    { id: 5, name: 'Operations', employees: 15, description: 'Business operations and administration' }
  ]);

  const [preferences, setPreferences] = useState({
    screeningThreshold: '75',
    emailNotifications: 'all',
    interviewDuration: '45',
    cvRetention: '12'
  });

  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [autoSaveTimeout, setAutoSaveTimeout] = useState(null);

  useEffect(() => {
    setupScrollEffects();
    fetchCompanyData();
    // Add CSS animations for notifications
    if (!document.querySelector('#company-modal-styles')) {
      const style = document.createElement('style');
      style.id = 'company-modal-styles';
      style.textContent = `
        @keyframes slideInFromRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutToRight {
          from { transform: translateX(0); opacity: 1; }
          to { transform: translateX(100%); opacity: 0; }
        }
        @keyframes fadeInOut {
          0% { opacity: 0; transform: translateY(-10px); }
          10% { opacity: 1; transform: translateY(0); }
          90% { opacity: 1; transform: translateY(0); }
          100% { opacity: 0; transform: translateY(-10px); }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(style);
    }
  }, []);


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

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  };

  const switchTab = (tabName) => {
    setActiveTab(tabName);
  };

  // Fetch company data from API
  const fetchCompanyData = async () => {
    setLoading(true);
    try {
      // Import apiService
      const apiService = (await import('../services/apiService')).default;

      // Fetch current user's company
      const response = await apiService.get('/companies/my-company');

      if (response && response.data) {
        const company = response.data;

        // Map API response to component state
        setCompanyData({
          id: company.id,
          company_name: company.company_name || 'Your Company',
          contact_email: company.contact_email || '',
          contact_phone: company.contact_phone || '',
          address: company.address || '',
          city: company.city || '',
          state: company.state || '',
          country: company.country || '',
          postal_code: company.postal_code || '',
          is_active: company.is_active,
          subscription_tier: company.subscription_tier || 'basic',
          max_users: company.max_users || 5,
          max_cv_uploads_monthly: company.max_cv_uploads_monthly || 100,
          // Legacy fields
          name: company.company_name || 'Your Company',
          industry: 'Technology & Software', // Can be added to API later
          founded: '', // Can be added to API later
          size: `Max ${company.max_users} users`,
          headquarters: company.city ? `${company.city}, ${company.state || company.country}` : '',
          timezone: '', // Can be added to API later
          description: company.address || 'No description available',
          mainPhone: company.contact_phone || '',
          hrPhone: company.contact_phone || '',
          mainEmail: company.contact_email || '',
          hrEmail: company.contact_email || '',
          website: '', // Can be added to API later
          linkedin: '', // Can be added to API later
          careersPage: '' // Can be added to API later
        });

        // Also load persisted data to merge
        loadPersistedData();
      }
    } catch (error) {
      console.error('Failed to fetch company data:', error);
      // Fallback to persisted data
      loadPersistedData();
    } finally {
      setLoading(false);
    }
  };

  // Load persisted data from localStorage
  const loadPersistedData = () => {
    try {
      // Load company logo
      const savedLogo = localStorage.getItem('company-logo');
      if (savedLogo) {
        setLogoPreview(savedLogo);
      }

      // Load company data (merge with existing data)
      const savedCompanyData = localStorage.getItem('company-data');
      if (savedCompanyData) {
        const parsedData = JSON.parse(savedCompanyData);
        setCompanyData(prevData => ({
          ...prevData,
          ...parsedData
        }));
      }

      // Load departments
      const savedDepartments = localStorage.getItem('company-departments');
      if (savedDepartments) {
        setDepartments(JSON.parse(savedDepartments));
      }

      // Load preferences
      const savedPreferences = localStorage.getItem('company-preferences');
      if (savedPreferences) {
        setPreferences(JSON.parse(savedPreferences));
      }
    } catch (error) {
      console.error('Failed to load persisted data:', error);
    }
  };

  // Save data to localStorage
  const saveToStorage = (key, data) => {
    try {
      if (typeof data === 'string') {
        localStorage.setItem(key, data);
      } else {
        localStorage.setItem(key, JSON.stringify(data));
      }
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  };

  const uploadLogo = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e) => handleLogoUpload(e.target.files);
    input.click();
  };

  const deleteLogo = () => {
    setConfirmDialog({
      show: true,
      title: 'Delete Company Logo?',
      message: 'Are you sure you want to delete the company logo? This action cannot be undone.',
      type: 'danger',
      onConfirm: () => {
        setLogoFile(null);
        setLogoPreview('🏢');
        localStorage.removeItem('company-logo');
        showToast('✓ Company logo deleted successfully!', 'success');
        setConfirmDialog({ ...confirmDialog, show: false });
      }
    });
  };

  const handleLogoUpload = (files) => {
    const file = files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        showToast('⚠️ File size must be less than 5MB', 'warning');
        return;
      }

      setLogoFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const logoData = e.target.result;
        setLogoPreview(logoData);
        // Save to localStorage
        saveToStorage('company-logo', logoData);
      };
      reader.readAsDataURL(file);

      // Simulate upload
      setTimeout(() => {
        showToast('✓ Company logo updated successfully!', 'success');
      }, 500);
    }
  };

  // Form validation functions
  const validateForm = (type, data) => {
    const newErrors = {};

    if (type === 'basic') {
      if (!data.name || data.name.trim().length < 2) {
        newErrors.name = 'Company name must be at least 2 characters';
      }
      if (!data.industry || data.industry.trim().length < 2) {
        newErrors.industry = 'Industry is required';
      }
      if (!data.founded || !/^\d{4}$/.test(data.founded)) {
        newErrors.founded = 'Please enter a valid 4-digit year';
      }
      if (!data.size) {
        newErrors.size = 'Company size is required';
      }
      if (!data.headquarters || data.headquarters.trim().length < 2) {
        newErrors.headquarters = 'Headquarters location is required';
      }
      if (!data.address || data.address.trim().length < 5) {
        newErrors.address = 'Complete address is required';
      }
      if (!data.country || data.country.trim().length < 2) {
        newErrors.country = 'Country is required';
      }
      if (!data.timezone) {
        newErrors.timezone = 'Timezone is required';
      }
      if (!data.description || data.description.trim().length < 20) {
        newErrors.description = 'Company description must be at least 20 characters';
      }
    } else if (type === 'contact') {
      const phoneRegex = /^\+?[\d\s\(\)-]{10,}$/;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const urlRegex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;

      if (!data.mainPhone || !phoneRegex.test(data.mainPhone)) {
        newErrors.mainPhone = 'Please enter a valid phone number';
      }
      if (!data.hrPhone || !phoneRegex.test(data.hrPhone)) {
        newErrors.hrPhone = 'Please enter a valid HR phone number';
      }
      if (!data.mainEmail || !emailRegex.test(data.mainEmail)) {
        newErrors.mainEmail = 'Please enter a valid email address';
      }
      if (!data.hrEmail || !emailRegex.test(data.hrEmail)) {
        newErrors.hrEmail = 'Please enter a valid HR email address';
      }
      if (data.website && !urlRegex.test(data.website)) {
        newErrors.website = 'Please enter a valid website URL';
      }
      if (data.linkedin && !urlRegex.test(data.linkedin)) {
        newErrors.linkedin = 'Please enter a valid LinkedIn URL';
      }
      if (data.careersPage && !urlRegex.test(data.careersPage)) {
        newErrors.careersPage = 'Please enter a valid careers page URL';
      }
    }

    return newErrors;
  };

  // Auto-save functionality
  const handleFormChange = (field, value) => {
    const updatedForm = { ...editForm, [field]: value };
    setEditForm(updatedForm);
    setHasUnsavedChanges(true);

    // Clear specific field error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }

    // Auto-save after 3 seconds of inactivity
    if (autoSaveTimeout) {
      clearTimeout(autoSaveTimeout);
    }

    const newTimeout = setTimeout(() => {
      const validationErrors = validateForm(modalType, updatedForm);
      if (Object.keys(validationErrors).length === 0) {
        autoSaveChanges(updatedForm);
      }
    }, 3000);

    setAutoSaveTimeout(newTimeout);
  };

  const autoSaveChanges = async (formData) => {
    // Silently save in background without showing loading state
    try {
      const apiService = (await import('../services/apiService')).default;

      if (modalType === 'basic' || modalType === 'contact') {
        // Prepare update data for API
        const updatePayload = {
          company_name: formData.name || companyData.company_name,
          contact_email: formData.mainEmail || companyData.contact_email,
          contact_phone: formData.mainPhone || companyData.contact_phone,
          address: formData.address || companyData.address,
          city: formData.headquarters ? formData.headquarters.split(',')[0].trim() : companyData.city,
          state: formData.headquarters ? formData.headquarters.split(',')[1]?.trim() : companyData.state,
          country: formData.country || companyData.country,
          postal_code: companyData.postal_code
        };

        // Call API to update company
        const response = await apiService.put(`/companies/${companyData.id}`, updatePayload);

        if (response && response.data) {
          const updatedCompany = response.data;

          // Update local state
          const updatedData = {
            ...companyData,
            id: updatedCompany.id,
            company_name: updatedCompany.company_name,
            contact_email: updatedCompany.contact_email,
            contact_phone: updatedCompany.contact_phone,
            address: updatedCompany.address,
            city: updatedCompany.city,
            state: updatedCompany.state,
            country: updatedCompany.country,
            postal_code: updatedCompany.postal_code,
            name: updatedCompany.company_name,
            mainEmail: updatedCompany.contact_email,
            hrEmail: formData.hrEmail || companyData.hrEmail,
            mainPhone: updatedCompany.contact_phone,
            hrPhone: formData.hrPhone || companyData.hrPhone,
            headquarters: updatedCompany.city ? `${updatedCompany.city}, ${updatedCompany.state || updatedCompany.country}` : companyData.headquarters,
            industry: formData.industry || companyData.industry,
            founded: formData.founded || companyData.founded,
            size: formData.size || companyData.size,
            timezone: formData.timezone || companyData.timezone,
            description: formData.description || companyData.description,
            website: formData.website || companyData.website,
            linkedin: formData.linkedin || companyData.linkedin,
            careersPage: formData.careersPage || companyData.careersPage
          };

          setCompanyData(updatedData);
          saveToStorage('company-data', updatedData);
        }
      } else if (modalType === 'preferences') {
        setPreferences(formData);
        saveToStorage('company-preferences', formData);
      }

      setHasUnsavedChanges(false);
      // Show brief "Auto-saved" indicator
      const indicator = document.createElement('div');
      indicator.textContent = 'Auto-saved';
      indicator.style.cssText = 'position:fixed;top:20px;right:20px;background:#22c55e;color:white;padding:8px 16px;border-radius:8px;font-size:14px;z-index:10000;animation:fadeInOut 2s ease;';
      document.body.appendChild(indicator);
      setTimeout(() => indicator.remove(), 2000);
    } catch (error) {
      console.error('Auto-save failed:', error);
      // Don't show error toast for auto-save failures to avoid annoying the user
    }
  };

  // Helper function to create form fields
  const createFormField = (fieldProps) => {
    const {
      id,
      label,
      type = 'text',
      value,
      onChange,
      required = false,
      placeholder = '',
      options = [],
      rows = 3,
      error = null,
      style = {}
    } = fieldProps;

    const baseInputStyle = {
      width: '100%',
      padding: '0.75rem',
      border: `1px solid ${error ? '#ef4444' : 'var(--border)'}`,
      borderRadius: '8px',
      fontSize: '0.875rem',
      backgroundColor: 'var(--surface)',
      color: 'var(--text-primary)',
      transition: 'border-color 0.2s ease',
      outline: 'none',
      ...style
    };

    return (
      <div className="form-group" style={{ marginBottom: '1rem' }}>
        <label
          htmlFor={id}
          style={{
            fontWeight: '500',
            marginBottom: '0.5rem',
            display: 'block',
            color: 'var(--text-primary)'
          }}
        >
          {label} {required && <span style={{ color: '#ef4444' }}>*</span>}
        </label>

        {type === 'select' ? (
          <select
            id={id}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={required}
            style={baseInputStyle}
            onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
            onBlur={(e) => e.target.style.borderColor = error ? '#ef4444' : 'var(--border)'}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : type === 'textarea' ? (
          <textarea
            id={id}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={required}
            placeholder={placeholder}
            rows={rows}
            style={{ ...baseInputStyle, resize: 'vertical' }}
            onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
            onBlur={(e) => e.target.style.borderColor = error ? '#ef4444' : 'var(--border)'}
          />
        ) : (
          <input
            type={type}
            id={id}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            required={required}
            placeholder={placeholder}
            style={baseInputStyle}
            onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
            onBlur={(e) => e.target.style.borderColor = error ? '#ef4444' : 'var(--border)'}
          />
        )}

        {error && (
          <span
            className="error-message"
            style={{
              color: '#ef4444',
              fontSize: '0.75rem',
              marginTop: '0.25rem',
              display: 'block'
            }}
          >
            {error}
          </span>
        )}
      </div>
    );
  };

  const openEditModal = (type) => {
    setModalType(type);
    setEditForm({ ...companyData, ...preferences });
    setErrors({});
    setHasUnsavedChanges(false);
    setShowModal(true);
  };

  const closeModal = () => {
    if (hasUnsavedChanges) {
      setConfirmDialog({
        show: true,
        title: 'Unsaved Changes',
        message: 'You have unsaved changes. Are you sure you want to close without saving?',
        type: 'warning',
        onConfirm: () => {
          if (autoSaveTimeout) {
            clearTimeout(autoSaveTimeout);
          }
          setShowModal(false);
          setModalType('');
          setEditForm({});
          setErrors({});
          setHasUnsavedChanges(false);
          setConfirmDialog({ ...confirmDialog, show: false });
        }
      });
      return;
    }

    if (autoSaveTimeout) {
      clearTimeout(autoSaveTimeout);
    }

    setShowModal(false);
    setModalType('');
    setEditForm({});
    setErrors({});
    setHasUnsavedChanges(false);
  };

  const saveChanges = async () => {
    // Validate form before saving
    const validationErrors = validateForm(modalType, editForm);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      // Scroll to first error
      setTimeout(() => {
        const firstErrorElement = document.querySelector('.error-message');
        if (firstErrorElement) {
          firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 100);
      return;
    }

    setSaving(true);

    try {
      // Import apiService
      const apiService = (await import('../services/apiService')).default;

      if (modalType === 'basic' || modalType === 'contact') {
        // Prepare update data for API
        const updatePayload = {
          company_name: editForm.name || companyData.company_name,
          contact_email: editForm.mainEmail || companyData.contact_email,
          contact_phone: editForm.mainPhone || companyData.contact_phone,
          address: editForm.address || companyData.address,
          city: editForm.headquarters ? editForm.headquarters.split(',')[0].trim() : companyData.city,
          state: editForm.headquarters ? editForm.headquarters.split(',')[1]?.trim() : companyData.state,
          country: editForm.country || companyData.country,
          postal_code: companyData.postal_code
        };

        // Call API to update company
        const response = await apiService.put(`/companies/${companyData.id}`, updatePayload);

        if (response && response.data) {
          const updatedCompany = response.data;

          // Update local state with API response and local fields
          const updatedData = {
            ...companyData,
            id: updatedCompany.id,
            company_name: updatedCompany.company_name,
            contact_email: updatedCompany.contact_email,
            contact_phone: updatedCompany.contact_phone,
            address: updatedCompany.address,
            city: updatedCompany.city,
            state: updatedCompany.state,
            country: updatedCompany.country,
            postal_code: updatedCompany.postal_code,
            // Update display fields
            name: updatedCompany.company_name,
            mainEmail: updatedCompany.contact_email,
            hrEmail: editForm.hrEmail || companyData.hrEmail,
            mainPhone: updatedCompany.contact_phone,
            hrPhone: editForm.hrPhone || companyData.hrPhone,
            headquarters: updatedCompany.city ? `${updatedCompany.city}, ${updatedCompany.state || updatedCompany.country}` : companyData.headquarters,
            // Keep local-only fields
            industry: editForm.industry || companyData.industry,
            founded: editForm.founded || companyData.founded,
            size: editForm.size || companyData.size,
            timezone: editForm.timezone || companyData.timezone,
            description: editForm.description || companyData.description,
            website: editForm.website || companyData.website,
            linkedin: editForm.linkedin || companyData.linkedin,
            careersPage: editForm.careersPage || companyData.careersPage
          };

          setCompanyData(updatedData);
          saveToStorage('company-data', updatedData);
          showToast('✓ Changes saved successfully!', 'success');
        }
      } else if (modalType === 'preferences') {
        const updatedPreferences = {
          screeningThreshold: editForm.screeningThreshold,
          emailNotifications: editForm.emailNotifications,
          interviewDuration: editForm.interviewDuration,
          cvRetention: editForm.cvRetention
        };
        setPreferences(updatedPreferences);
        saveToStorage('company-preferences', updatedPreferences);
        showToast('✓ Preferences saved successfully!', 'success');
      }

      setSaving(false);
      setHasUnsavedChanges(false);
      closeModal();

    } catch (error) {
      setSaving(false);
      console.error('Save failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save changes. Please try again.';
      showToast(`❌ ${errorMessage}`, 'error');
    }
  };

  const addDepartment = () => {
    const name = prompt('Enter department name:');
    const employees = prompt('Enter number of employees:');
    const description = prompt('Enter department description:');

    if (name && employees && description) {
      const newDept = {
        id: Date.now(),
        name,
        employees: parseInt(employees),
        description
      };
      const updatedDepartments = [...departments, newDept];
      setDepartments(updatedDepartments);
      saveToStorage('company-departments', updatedDepartments);
      showToast('✓ Department added successfully!', 'success');
    }
  };

  const editDepartment = (dept) => {
    const name = prompt('Edit department name:', dept.name);
    const employees = prompt('Edit number of employees:', dept.employees);
    const description = prompt('Edit department description:', dept.description);

    if (name && employees && description) {
      const updatedDepartments = departments.map(d =>
        d.id === dept.id
          ? { ...d, name, employees: parseInt(employees), description }
          : d
      );
      setDepartments(updatedDepartments);
      saveToStorage('company-departments', updatedDepartments);
      showToast('✓ Department updated successfully!', 'success');
    }
  };

  const deleteDepartment = (deptId) => {
    setConfirmDialog({
      show: true,
      title: 'Delete Department?',
      message: 'Are you sure you want to delete this department? This action cannot be undone.',
      type: 'danger',
      onConfirm: () => {
        const updatedDepartments = departments.filter(d => d.id !== deptId);
        setDepartments(updatedDepartments);
        saveToStorage('company-departments', updatedDepartments);
        showToast('✓ Department deleted successfully!', 'success');
        setConfirmDialog({ ...confirmDialog, show: false });
      }
    });
  };

  // Keyboard shortcuts for modal - moved after function definitions
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (!showModal) return;

      switch (event.key) {
        case 'Escape':
          closeModal();
          break;
        case 's':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            saveChanges();
          }
          break;
        case 'Enter':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            saveChanges();
          }
          break;
      }
    };

    if (showModal) {
      document.addEventListener('keydown', handleKeyDown);
      // Focus management for accessibility
      const modal = document.querySelector('.modal-content');
      if (modal) {
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'modal-title');

        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
          setTimeout(() => firstInput.focus(), 100);
        }
      }
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showModal]);

  return (
    <div>
      <section className="profile-header" style={{ paddingTop: '9rem' }}>
        <div className="container">
          <h1>Company Profile</h1>
          <p>Manage your organization's information and Resumify subscription settings</p>
        </div>
      </section>

      <main className="container">
        <div className="profile-content">
          {/* Sidebar */}
          <div className="profile-sidebar">
            <div className="company-logo-card animate-on-scroll">
              <div className="company-logo" style={{ cursor: 'pointer', position: 'relative' }} onClick={uploadLogo}>
                {typeof logoPreview === 'string' && logoPreview.startsWith('data:') ? (
                  <img src={logoPreview} alt="Company Logo" style={{ width: '80px', height: '80px', objectFit: 'cover', borderRadius: '50%' }} />
                ) : (
                  <span style={{ fontSize: '3rem' }}>{logoPreview}</span>
                )}
                {/* Delete button overlay for uploaded logos */}
                {typeof logoPreview === 'string' && logoPreview.startsWith('data:') && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteLogo();
                    }}
                    style={{
                      position: 'absolute',
                      top: '-5px',
                      right: '-5px',
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                    }}
                    title="Delete logo"
                  >
                    ×
                  </button>
                )}
              </div>
              <h3>{loading ? 'Loading...' : (companyData.company_name || companyData.name)}</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <button
                  className="upload-logo-btn"
                  onClick={uploadLogo}
                  style={{
                    padding: '0.5rem 1rem',
                    border: '1px solid var(--primary)',
                    borderRadius: '8px',
                    backgroundColor: 'var(--primary)',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  {typeof logoPreview === 'string' && logoPreview.startsWith('data:') ? 'Change Logo' : 'Upload Logo'}
                </button>
                {typeof logoPreview === 'string' && logoPreview.startsWith('data:') && (
                  <button
                    onClick={deleteLogo}
                    style={{
                      padding: '0.5rem 1rem',
                      border: '1px solid #ef4444',
                      borderRadius: '8px',
                      backgroundColor: 'transparent',
                      color: '#ef4444',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}
                  >
                    Delete Logo
                  </button>
                )}
              </div>
            </div>

          </div>

          {/* Main Profile */}
          <div className="main-profile animate-on-scroll animate-delay-2">
            <div className="profile-tabs" style={{ justifyContent: 'center' }}>
              <button
                className={`tab-btn ${activeTab === 'basic' ? 'active' : ''}`}
                onClick={() => switchTab('basic')}
              >
                Company Info
              </button>
              <button
                className={`tab-btn ${activeTab === 'contact' ? 'active' : ''}`}
                onClick={() => switchTab('contact')}
              >
                Contact Details
              </button>
              <button
                className={`tab-btn ${activeTab === 'departments' ? 'active' : ''}`}
                onClick={() => switchTab('departments')}
              >
                Departments
              </button>
            </div>

            {/* Basic Info Tab */}
            {activeTab === 'basic' && (
              <div className="tab-content active">
                <div className="info-grid">
                  <div className="info-section">
                    <h4>Company Information</h4>
                    <div className="info-item">
                      <span className="info-label">Company Name</span>
                      <span className="info-value">{companyData.name}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Industry</span>
                      <span className="info-value">{companyData.industry}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Founded</span>
                      <span className="info-value">{companyData.founded}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Company Size</span>
                      <span className="info-value">{companyData.size}</span>
                    </div>
                  </div>

                  <div className="info-section">
                    <h4>Location Details</h4>
                    <div className="info-item">
                      <span className="info-label">Headquarters</span>
                      <span className="info-value">{companyData.headquarters}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Address</span>
                      <span className="info-value">{companyData.address}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Country</span>
                      <span className="info-value">{companyData.country}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Time Zone</span>
                      <span className="info-value">{companyData.timezone}</span>
                    </div>
                  </div>
                </div>

                <div className="info-section">
                  <h4>About Company</h4>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginTop: '1rem' }}>
                    {companyData.description}
                  </p>
                </div>

                <button className="edit-btn" onClick={() => openEditModal('basic')}>Edit Company Information</button>
              </div>
            )}

            {/* Contact Tab */}
            {activeTab === 'contact' && (
              <div className="tab-content active">
                <div className="info-grid">
                  <div className="info-section">
                    <h4>Contact Information</h4>
                    <div className="info-item">
                      <span className="info-label">Main Phone</span>
                      <span className="info-value">{companyData.mainPhone}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">HR Department</span>
                      <span className="info-value">{companyData.hrPhone}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Main Email</span>
                      <span className="info-value">{companyData.mainEmail}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">HR Email</span>
                      <span className="info-value">{companyData.hrEmail}</span>
                    </div>
                  </div>

                  <div className="info-section">
                    <h4>Online Presence</h4>
                    <div className="info-item">
                      <span className="info-label">Website</span>
                      <span className="info-value">{companyData.website}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">LinkedIn</span>
                      <span className="info-value">{companyData.linkedin}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Careers Page</span>
                      <span className="info-value">{companyData.careersPage}</span>
                    </div>
                  </div>
                </div>

                <button className="edit-btn" onClick={() => openEditModal('contact')}>Edit Contact Information</button>
              </div>
            )}

            {/* Departments Tab */}
            {activeTab === 'departments' && (
              <div className="tab-content active">
                <div className="info-section">
                  <h4>Department Structure</h4>
                  <div className="departments-list">
                    {departments.map(dept => (
                      <div key={dept.id} className="department-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', padding: '1rem', border: '1px solid var(--border)', borderRadius: '8px' }}>
                        <div>
                          <h5 style={{ margin: '0 0 0.5rem 0' }}>{dept.name}</h5>
                          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{dept.employees} employees - {dept.description}</p>
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            onClick={() => editDepartment(dept)}
                            style={{ padding: '0.5rem 1rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteDepartment(dept.id)}
                            style={{ padding: '0.5rem 1rem', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button className="edit-btn" onClick={addDepartment}>Add Department</button>
                </div>
              </div>
            )}

          </div>
        </div>
      </main>

      {/* Edit Modal */}
      {showModal && (
        <div
          className="modal"
          style={{
            display: 'flex',
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1000,
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem'
          }}
          onClick={closeModal}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: '700px',
              width: '100%',
              maxHeight: '90vh',
              backgroundColor: 'var(--surface)',
              borderRadius: '16px',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              border: '1px solid var(--border)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
          >
            {/* Fixed Header */}
            <div
              className="modal-header"
              style={{
                padding: '1.5rem',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backgroundColor: 'var(--surface)',
                borderRadius: '16px 16px 0 0'
              }}
            >
              <h2 id="modal-title" style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.5rem', fontWeight: '600' }}>
                {modalType === 'basic' && 'Edit Company Information'}
                {modalType === 'contact' && 'Edit Contact Information'}
                {modalType === 'preferences' && 'Update Preferences'}
              </h2>
              <button
                onClick={closeModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: 'var(--text-secondary)',
                  padding: '0.5rem',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '32px',
                  height: '32px'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = 'var(--surface-hover)'}
                onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
              >
                ×
              </button>
            </div>

            {/* Scrollable Body */}
            <div
              className="modal-body"
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '1.5rem',
                maxHeight: 'calc(90vh - 140px)' // Account for header and footer
              }}
            >

              {/* Basic Info Form */}
              {modalType === 'basic' && (
                <form>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                    {createFormField({
                      id: 'companyName',
                      label: 'Company Name',
                      value: editForm.name || '',
                      onChange: (value) => handleFormChange('name', value),
                      required: true,
                      error: errors.name,
                      placeholder: 'Enter company name'
                    })}

                    {createFormField({
                      id: 'industry',
                      label: 'Industry',
                      value: editForm.industry || '',
                      onChange: (value) => handleFormChange('industry', value),
                      required: true,
                      error: errors.industry,
                      placeholder: 'e.g. Technology & Software'
                    })}

                    {createFormField({
                      id: 'founded',
                      label: 'Founded Year',
                      value: editForm.founded || '',
                      onChange: (value) => handleFormChange('founded', value),
                      required: true,
                      error: errors.founded,
                      placeholder: 'e.g. 2010'
                    })}

                    {createFormField({
                      id: 'companySize',
                      label: 'Company Size',
                      type: 'select',
                      value: editForm.size || '',
                      onChange: (value) => handleFormChange('size', value),
                      required: true,
                      error: errors.size,
                      options: [
                        { value: '', label: 'Select company size' },
                        { value: '1-10 employees', label: '1-10 employees' },
                        { value: '11-50 employees', label: '11-50 employees' },
                        { value: '51-200 employees', label: '51-200 employees' },
                        { value: '201-500 employees', label: '201-500 employees' },
                        { value: '501-1000 employees', label: '501-1000 employees' },
                        { value: '1000+ employees', label: '1000+ employees' }
                      ]
                    })}

                    {createFormField({
                      id: 'headquarters',
                      label: 'Headquarters',
                      value: editForm.headquarters || '',
                      onChange: (value) => handleFormChange('headquarters', value),
                      required: true,
                      error: errors.headquarters,
                      placeholder: 'e.g. San Francisco, CA'
                    })}

                    {createFormField({
                      id: 'country',
                      label: 'Country',
                      value: editForm.country || '',
                      onChange: (value) => handleFormChange('country', value),
                      required: true,
                      error: errors.country,
                      placeholder: 'e.g. United States'
                    })}
                  </div>

                  {createFormField({
                    id: 'address',
                    label: 'Full Address',
                    value: editForm.address || '',
                    onChange: (value) => handleFormChange('address', value),
                    required: true,
                    error: errors.address,
                    placeholder: 'Complete business address'
                  })}

                  {createFormField({
                    id: 'timezone',
                    label: 'Time Zone',
                    type: 'select',
                    value: editForm.timezone || '',
                    onChange: (value) => handleFormChange('timezone', value),
                    required: true,
                    error: errors.timezone,
                    options: [
                      { value: '', label: 'Select timezone' },
                      { value: 'EST (UTC-5)', label: 'EST (UTC-5)' },
                      { value: 'CST (UTC-6)', label: 'CST (UTC-6)' },
                      { value: 'MST (UTC-7)', label: 'MST (UTC-7)' },
                      { value: 'PST (UTC-8)', label: 'PST (UTC-8)' },
                      { value: 'GMT (UTC+0)', label: 'GMT (UTC+0)' },
                      { value: 'CET (UTC+1)', label: 'CET (UTC+1)' }
                    ]
                  })}

                  {createFormField({
                    id: 'description',
                    label: 'About Company',
                    type: 'textarea',
                    value: editForm.description || '',
                    onChange: (value) => handleFormChange('description', value),
                    required: true,
                    error: errors.description,
                    placeholder: 'Tell us about your company, mission, and values...',
                    rows: 4
                  })}
                </form>
              )}

              {/* Contact Info Form */}
              {modalType === 'contact' && (
                <form>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                    {createFormField({
                      id: 'mainPhone',
                      label: 'Main Phone',
                      type: 'tel',
                      value: editForm.mainPhone || '',
                      onChange: (value) => handleFormChange('mainPhone', value),
                      required: true,
                      error: errors.mainPhone,
                      placeholder: '+1 (555) 123-4567'
                    })}

                    {createFormField({
                      id: 'hrPhone',
                      label: 'HR Department Phone',
                      type: 'tel',
                      value: editForm.hrPhone || '',
                      onChange: (value) => handleFormChange('hrPhone', value),
                      required: true,
                      error: errors.hrPhone,
                      placeholder: '+1 (555) 123-4568'
                    })}

                    {createFormField({
                      id: 'mainEmail',
                      label: 'Main Email',
                      type: 'email',
                      value: editForm.mainEmail || '',
                      onChange: (value) => handleFormChange('mainEmail', value),
                      required: true,
                      error: errors.mainEmail,
                      placeholder: 'info@company.com'
                    })}

                    {createFormField({
                      id: 'hrEmail',
                      label: 'HR Email',
                      type: 'email',
                      value: editForm.hrEmail || '',
                      onChange: (value) => handleFormChange('hrEmail', value),
                      required: true,
                      error: errors.hrEmail,
                      placeholder: 'hr@company.com'
                    })}

                    {createFormField({
                      id: 'website',
                      label: 'Company Website',
                      type: 'url',
                      value: editForm.website || '',
                      onChange: (value) => handleFormChange('website', value),
                      error: errors.website,
                      placeholder: 'https://www.company.com'
                    })}

                    {createFormField({
                      id: 'linkedin',
                      label: 'LinkedIn Profile',
                      type: 'url',
                      value: editForm.linkedin || '',
                      onChange: (value) => handleFormChange('linkedin', value),
                      error: errors.linkedin,
                      placeholder: 'https://linkedin.com/company/yourcompany'
                    })}
                  </div>

                  {createFormField({
                    id: 'careersPage',
                    label: 'Careers Page',
                    type: 'url',
                    value: editForm.careersPage || '',
                    onChange: (value) => handleFormChange('careersPage', value),
                    error: errors.careersPage,
                    placeholder: 'https://www.company.com/careers'
                  })}
                </form>
              )}

              {/* Preferences Form */}
              {modalType === 'preferences' && (
                <form>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    {createFormField({
                      id: 'screeningThreshold',
                      label: 'Auto-screening Threshold',
                      type: 'select',
                      value: editForm.screeningThreshold || preferences.screeningThreshold,
                      onChange: (value) => handleFormChange('screeningThreshold', value),
                      options: [
                        { value: '75', label: '75% match or higher' },
                        { value: '80', label: '80% match or higher' },
                        { value: '85', label: '85% match or higher' }
                      ]
                    })}

                    {createFormField({
                      id: 'emailNotifications',
                      label: 'Email Notifications',
                      type: 'select',
                      value: editForm.emailNotifications || preferences.emailNotifications,
                      onChange: (value) => handleFormChange('emailNotifications', value),
                      options: [
                        { value: 'all', label: 'All notifications' },
                        { value: 'important', label: 'Important only' },
                        { value: 'disabled', label: 'Disabled' }
                      ]
                    })}

                    {createFormField({
                      id: 'interviewDuration',
                      label: 'Default Interview Duration',
                      type: 'select',
                      value: editForm.interviewDuration || preferences.interviewDuration,
                      onChange: (value) => handleFormChange('interviewDuration', value),
                      options: [
                        { value: '30', label: '30 minutes' },
                        { value: '45', label: '45 minutes' },
                        { value: '60', label: '60 minutes' },
                        { value: '90', label: '90 minutes' }
                      ]
                    })}

                    {createFormField({
                      id: 'cvRetention',
                      label: 'CV Retention Period',
                      type: 'select',
                      value: editForm.cvRetention || preferences.cvRetention,
                      onChange: (value) => handleFormChange('cvRetention', value),
                      options: [
                        { value: '6', label: '6 months' },
                        { value: '12', label: '12 months' },
                        { value: '24', label: '24 months' },
                        { value: '36', label: '36 months' }
                      ]
                    })}
                  </div>

                  <div style={{
                    marginTop: '2rem',
                    padding: '1rem',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    borderRadius: '8px'
                  }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)', fontSize: '0.875rem', fontWeight: '600' }}>
                      💡 Pro Tips
                    </h4>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                      <li>Higher screening thresholds reduce manual review time but may miss good candidates</li>
                      <li>Email notifications help you stay responsive to candidate applications</li>
                      <li>Longer interview slots allow for more thorough assessments</li>
                      <li>Extended CV retention helps with compliance and future hiring needs</li>
                    </ul>
                  </div>
                </form>
              )}
            </div>

            {/* Fixed Footer */}
            <div
              className="modal-footer"
              style={{
                padding: '1.5rem',
                borderTop: '1px solid var(--border)',
                backgroundColor: 'var(--surface)',
                borderRadius: '0 0 16px 16px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '1rem'
              }}
            >
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <div style={{ marginBottom: '0.25rem' }}>
                  {modalType === 'basic' && 'Update your company details to keep your profile current'}
                  {modalType === 'contact' && 'Ensure your contact information is accurate and up-to-date'}
                  {modalType === 'preferences' && 'Customize Resumify settings to match your workflow'}
                </div>
                <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>
                  💾 Auto-saves every 3 seconds • <kbd style={{ backgroundColor: 'rgba(0,0,0,0.1)', padding: '2px 4px', borderRadius: '3px', fontSize: '0.7rem' }}>Ctrl+S</kbd> to save • <kbd style={{ backgroundColor: 'rgba(0,0,0,0.1)', padding: '2px 4px', borderRadius: '3px', fontSize: '0.7rem' }}>Esc</kbd> to close
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={closeModal}
                  disabled={saving}
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    backgroundColor: 'var(--surface)',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    if (!saving) {
                      e.target.style.backgroundColor = 'var(--surface-hover)';
                      e.target.style.borderColor = 'var(--border-hover)';
                    }
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = 'var(--surface)';
                    e.target.style.borderColor = 'var(--border)';
                  }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={saveChanges}
                  disabled={saving}
                  style={{
                    padding: '0.75rem 2rem',
                    border: 'none',
                    borderRadius: '8px',
                    backgroundColor: saving ? '#6B7280' : 'var(--primary)',
                    color: 'white',
                    cursor: saving ? 'not-allowed' : 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                  onMouseOver={(e) => {
                    if (!saving) {
                      e.target.style.backgroundColor = 'var(--primary-hover)';
                      e.target.style.transform = 'translateY(-1px)';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!saving) {
                      e.target.style.backgroundColor = 'var(--primary)';
                      e.target.style.transform = 'translateY(0)';
                    }
                  }}
                >
                  {saving && <div style={{ width: '16px', height: '16px', border: '2px solid #ffffff', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>}
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
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
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog({ ...confirmDialog, show: false })}
      />
    </div>
  );
}

export default Company;