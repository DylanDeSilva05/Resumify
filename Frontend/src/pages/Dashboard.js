import React, { useState, useEffect } from 'react';
import apiService from '../services/apiService';
import { useHeaderScroll } from '../hooks/useHeaderScroll';
import { useToast } from '../contexts/ToastContext';
import ConfirmDialog from '../components/ConfirmDialog';
import SettingsNotification from '../components/SettingsNotification';

function Dashboard() {
  const { showToast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({ show: false, value: 0 });
  const [candidates, setCandidates] = useState({ total: 0, shortlisted: 0, rejected: 0 });
  const [jobForm, setJobForm] = useState({ title: '', requirements: '' });
  const [showCandidatesModal, setShowCandidatesModal] = useState(false);
  const [showInterviewModal, setShowInterviewModal] = useState(false);
  const [modalData, setModalData] = useState({ status: '', candidates: [] });
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [parsedCandidates, setParsedCandidates] = useState([]);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [interviewForm, setInterviewForm] = useState({
    datetime: '',
    type: 'video',
    notes: ''
  });
  const [emailPreview, setEmailPreview] = useState(null);
  const [showCVDetailsModal, setShowCVDetailsModal] = useState(false);
  const [selectedCandidateDetails, setSelectedCandidateDetails] = useState(null);
  const [showEmailPreviewModal, setShowEmailPreviewModal] = useState(false);
  const [emailToSend, setEmailToSend] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    title: '',
    message: '',
    type: 'warning',
    onConfirm: null
  });

  // Use custom hook for header scroll effect
  useHeaderScroll();

  // Initialize auth
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      // API auth logic will go here
      console.log('Initializing auth...');
    } catch (error) {
      console.error('Auth failed:', error);
    }
  };

  const goToStep = (stepNumber) => {
    setCurrentStep(stepNumber);
    setTimeout(() => {
      const targetStep = document.getElementById(`step${stepNumber}`);
      if (targetStep) {
        targetStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  const uploadCVs = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.doc,.docx';
    input.onchange = (e) => handleFileUpload(e.target.files);
    input.click();
  };

  const handleFileUpload = async (files) => {
    const filesArray = Array.from(files);
    setUploadedFiles(filesArray);

    // Just store the files, don't upload yet - we'll upload and analyze together when form is submitted
    console.log('Files selected:', filesArray.map(f => f.name));

    // Show success toast notification
    showToast(`✓ ${filesArray.length} file${filesArray.length > 1 ? 's' : ''} uploaded successfully!`, 'success');
  };

  // Toast notification is now provided by useToast() context hook

  const processAndAnalyze = async (e) => {
    e.preventDefault();

    // ✅ ENHANCED VALIDATION: Check for uploaded files
    if (uploadedFiles.length === 0) {
      showToast('⚠️ Please upload at least one CV file before analyzing', 'warning');
      goToStep(1);
      return;
    }

    // ✅ ENHANCED VALIDATION: Check job title
    if (!jobForm.title || jobForm.title.trim() === '') {
      showToast('⚠️ Please enter a job title', 'warning');
      return;
    }

    // ✅ ENHANCED VALIDATION: Check job requirements
    if (!jobForm.requirements || jobForm.requirements.trim() === '') {
      showToast('⚠️ Please enter job requirements', 'warning');
      return;
    }

    // ✅ NEW VALIDATION: Check requirements length for quality
    if (jobForm.requirements.trim().length < 50) {
      const proceed = window.confirm(
        `⚠️ Job requirements seem brief (${jobForm.requirements.trim().length} characters).\n\nFor better matching accuracy, consider adding:\n• Required skills and experience\n• Key responsibilities\n• Qualifications needed\n\nProceed with current requirements?`
      );
      if (!proceed) {
        return;
      }
    }

    try {
      setIsAnalyzing(true);
      setUploadProgress({ show: true, value: 0 });

      // Simulate progressive updates for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev.value < 90) {
            return { ...prev, value: prev.value + 10 };
          }
          return prev;
        });
      }, 500);

      console.log('Starting upload with files:', uploadedFiles);
      console.log('Job form:', jobForm);

      // Use the combined upload and analyze endpoint
      const analysisData = await apiService.uploadAndAnalyzeCVs(
        uploadedFiles,
        jobForm.title,
        jobForm.requirements
      );

      clearInterval(progressInterval);
      setUploadProgress({ show: true, value: 100 });

      // Brief delay to show 100% completion
      await new Promise(resolve => setTimeout(resolve, 500));

      setUploadProgress({ show: false, value: 0 });

      // Set analysis results
      setAnalysisResults(analysisData.candidates || []);

      // Debug: Log full candidate data to see what's available
      console.log('============ ANALYSIS RESULTS DEBUG ============');
      console.log('Job Title:', jobForm.title);
      console.log('Job Requirements:', jobForm.requirements);
      console.log('Total Candidates:', analysisData.total);
      console.log('Shortlisted:', analysisData.shortlisted);
      console.log('Rejected:', analysisData.rejected);
      console.log('\nFull analysis data:', JSON.stringify(analysisData, null, 2));
      console.log('================================================');

      // Calculate statistics from real analysis results
      const total = analysisData.total || 0;
      const shortlisted = analysisData.shortlisted || 0;
      const rejected = analysisData.rejected || 0;

      setCandidates({ total, shortlisted, rejected });
      goToStep(3);

      console.log('Analysis results:', analysisData);
      showToast(`✓ Analysis complete! Found ${total} candidates (${shortlisted} shortlisted).`, 'success');
    } catch (error) {
      console.error('Failed to analyze candidates:', error);
      showToast('❌ Failed to analyze candidates. Please try again.', 'error');
      setUploadProgress({ show: false, value: 0 });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Helper function to generate enhanced summary for HR quick view
  const generateEnhancedSummary = (candidate) => {
    const summaryParts = [];
    const matchScore = Math.round(candidate.match_score || 0);

    // 1. Match Quality Assessment (opening)
    if (matchScore >= 80) {
      summaryParts.push(`⭐ Excellent ${matchScore}% match`);
    } else if (matchScore >= 70) {
      summaryParts.push(`✓ Strong ${matchScore}% match`);
    } else if (matchScore >= 60) {
      summaryParts.push(`${matchScore}% match`);
    } else {
      summaryParts.push(`${matchScore}% match`);
    }

    // 2. Key Strengths (from AI analysis)
    if (candidate.strengths && candidate.strengths.length > 0) {
      const strengthsList = candidate.strengths.slice(0, 3).join(', ');
      summaryParts.push(`Strengths: ${strengthsList}`);
    }

    // 3. Areas of Concern (from AI analysis)
    if (candidate.concerns && candidate.concerns.length > 0) {
      const concernsList = candidate.concerns.slice(0, 2).join(', ');
      summaryParts.push(`Considerations: ${concernsList}`);
    }

    // Fallback: Try to extract from detailed fields if available
    if (summaryParts.length === 1) { // Only has match score
      // Try work experience
      if (candidate.work_experience && candidate.work_experience.length > 0) {
        const latestExp = candidate.work_experience[0];
        const role = latestExp.title || latestExp.position;
        const company = latestExp.company;
        if (role && company) {
          summaryParts.push(`${role} at ${company}`);
        }
      }

      // Try skills
      if (candidate.skills && candidate.skills.length > 0) {
        const skillsList = candidate.skills.slice(0, 4).map(skill =>
          typeof skill === 'string' ? skill : skill.name || skill.skill
        ).filter(Boolean).join(', ');
        if (skillsList) {
          summaryParts.push(`Skills: ${skillsList}`);
        }
      }

      // Try education
      if (candidate.education && candidate.education.length > 0) {
        const edu = candidate.education[0];
        const degree = edu.degree || edu.qualification;
        if (degree) {
          summaryParts.push(degree);
        }
      }
    }

    // Final fallback
    if (summaryParts.length === 1) {
      return `${summaryParts[0]} - Click "View Details" for complete candidate information`;
    }

    return summaryParts.join(' • ');
  };

  // Helper function to generate candidate summary
  const generateCandidateSummary = (candidate) => {
    const parts = [];

    // Calculate total years of experience
    let totalYears = 0;
    if (candidate.work_experience && candidate.work_experience.length > 0) {
      candidate.work_experience.forEach(exp => {
        if (exp.duration) {
          const years = exp.duration.match(/(\d+)\s*year/i);
          if (years) totalYears += parseInt(years[1]);
        }
      });
    }

    // Build comprehensive professional summary
    if (candidate.work_experience && candidate.work_experience.length > 0) {
      const exp = candidate.work_experience[0];
      const title = exp.title || exp.position || 'Professional';
      const company = exp.company || 'various organizations';

      if (totalYears > 0) {
        parts.push(`${title} with ${totalYears}+ years of experience at ${company}`);
      } else {
        parts.push(`${title} with proven experience at ${company}`);
      }

      // Add key responsibilities if available
      if (exp.responsibilities && exp.responsibilities.length > 0) {
        const keyResp = exp.responsibilities.slice(0, 2).join(', ');
        if (keyResp) {
          parts.push(`Specialized in ${keyResp}`);
        }
      }
    }

    // Add comprehensive skills summary
    if (candidate.skills && candidate.skills.length > 0) {
      const allSkills = candidate.skills.map(skill =>
        typeof skill === 'string' ? skill : skill.name || skill.skill
      ).filter(Boolean);

      if (allSkills.length > 0) {
        const skillCount = allSkills.length;
        const topSkills = allSkills.slice(0, 5).join(', ');

        if (skillCount > 5) {
          parts.push(`Proficient in ${topSkills}, and ${skillCount - 5} more technologies`);
        } else {
          parts.push(`Skilled in ${topSkills}`);
        }
      }
    }

    // Add education summary with more details
    if (candidate.education && candidate.education.length > 0) {
      const edu = candidate.education[0];
      const degree = edu.degree || edu.qualification;
      const institution = edu.institution || edu.school;
      const field = edu.field;

      if (degree && institution) {
        if (field) {
          parts.push(`Holds ${degree} in ${field} from ${institution}`);
        } else {
          parts.push(`${degree} graduate from ${institution}`);
        }
      }
    }

    // Add certifications if available
    if (candidate.certifications && candidate.certifications.length > 0) {
      const certCount = candidate.certifications.length;
      const certName = typeof candidate.certifications[0] === 'string'
        ? candidate.certifications[0]
        : candidate.certifications[0].name;

      if (certCount > 1) {
        parts.push(`Certified professional with ${certCount} certifications including ${certName}`);
      } else {
        parts.push(`Certified in ${certName}`);
      }
    }

    // Add match assessment
    if (candidate.match_score >= 80) {
      parts.push(`Excellent match for the position with ${Math.round(candidate.match_score)}% compatibility`);
    } else if (candidate.match_score >= 70) {
      parts.push(`Strong candidate with ${Math.round(candidate.match_score)}% match score`);
    }

    // Fallback summary based on match score
    if (parts.length === 0) {
      return `Experienced professional with ${candidate.match_score >= 70 ? 'strong background in relevant technologies and proven track record' : 'diverse skill set and experience across multiple domains'}. Match score: ${Math.round(candidate.match_score)}%`;
    }

    return parts.join('. ') + '.';
  };

  const showCandidates = (status) => {
    let filteredResults = [];

    if (status === 'total') {
      filteredResults = analysisResults;
    } else {
      filteredResults = analysisResults.filter(result => result.match_status === status);
    }

    // Map analysis results to display format with enhanced summary
    const candidatesData = filteredResults.map(result => {
      // Generate enhanced summary with full candidate data
      const enhancedSummary = generateEnhancedSummary(result);

      // Debug logs
      console.log('Candidate:', result.name);
      console.log('Backend summary:', result.summary);
      console.log('Enhanced summary:', enhancedSummary);
      console.log('Final summary used:', enhancedSummary);

      return {
        id: result.id,
        name: result.name ||
              result.candidate_name ||
              (result.email ? result.email.split('@')[0].replace(/[._]/g, ' ') : null) ||
              `Candidate ${result.id}`,
        email: result.email || 'N/A',
        match_score: Math.round(result.match_score || 0),
        // Use our enhanced summary instead of backend's generic one
        summary: enhancedSummary
      };
    });

    setModalData({
      status: status.charAt(0).toUpperCase() + status.slice(1),
      candidates: candidatesData
    });
    setShowCandidatesModal(true);
  };

  const openInterviewModal = async (candidate) => {
    setSelectedCandidate(candidate);
    // Set default interview datetime to tomorrow at 10 AM
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0, 0, 0);
    const defaultForm = {
      datetime: tomorrow.toISOString().slice(0, 16),
      type: 'video',
      notes: ''
    };
    setInterviewForm(defaultForm);
    setShowInterviewModal(true);

    // Generate email preview
    await generateEmailPreview(candidate, defaultForm);
  };

  const generateEmailPreview = async (candidate, form) => {
    try {
      const preview = await apiService.previewInterviewEmail(
        candidate.id,
        form.datetime,
        form.type
      );
      setEmailPreview(preview);
    } catch (error) {
      console.error('Failed to generate email preview:', error);
      setEmailPreview(null);
    }
  };

  const scheduleInterview = async (e) => {
    e.preventDefault();
    if (!selectedCandidate) return;

    // ✅ VALIDATION: Check if datetime is provided
    if (!interviewForm.datetime) {
      showToast('⚠️ Please select a date and time for the interview', 'warning');
      return;
    }

    // ✅ VALIDATION: Check if datetime is in the past
    const selectedDate = new Date(interviewForm.datetime);
    const now = new Date();

    if (selectedDate < now) {
      showToast('⚠️ Cannot schedule interview in the past. Please select a future date and time.', 'error');
      return;
    }

    // ✅ VALIDATION: Check if datetime is within reasonable range (not more than 1 year ahead)
    const oneYearFromNow = new Date();
    oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);

    if (selectedDate > oneYearFromNow) {
      showToast('⚠️ Cannot schedule interview more than 1 year in advance', 'warning');
      return;
    }

    // ✅ VALIDATION: Check if datetime is during business hours (8 AM - 6 PM)
    const hours = selectedDate.getHours();
    if (hours < 8 || hours >= 18) {
      const proceed = window.confirm(
        `⚠️ The selected time (${selectedDate.toLocaleTimeString()}) is outside typical business hours (8 AM - 6 PM).\n\nDo you want to proceed anyway?`
      );
      if (!proceed) return;
    }

    try {
      // Call API to schedule interview
      const result = await apiService.scheduleInterview(
        selectedCandidate.id,
        interviewForm.datetime,
        interviewForm.type
      );

      let message = `✅ Interview scheduled successfully with ${selectedCandidate.name}!`;
      if (result.email_sent) {
        message += ' 📧 Email invitation sent to candidate.';
        showToast(message, 'success');
      } else {
        message += ' ⚠️ Email could not be sent.';
        showToast(message, 'warning');
      }

      setShowInterviewModal(false);
      setShowCandidatesModal(false);
      setEmailPreview(null);

      // ✅ IMPROVEMENT: Reset interview form after successful scheduling
      setInterviewForm({
        datetime: '',
        type: 'video',
        notes: ''
      });
    } catch (error) {
      console.error('Failed to schedule interview:', error);
      showToast('❌ Failed to schedule interview. Please try again.', 'error');
    }
  };

  const viewCandidateDetails = async (candidate) => {
    // Find full candidate data from analysis results
    const fullCandidateData = analysisResults.find(result => result.id === candidate.id);

    if (fullCandidateData) {
      console.log('Full candidate data:', JSON.stringify(fullCandidateData, null, 2));
      console.log('Has work_experience:', fullCandidateData.work_experience);
      console.log('Has skills:', fullCandidateData.skills);
      console.log('Has education:', fullCandidateData.education);
      console.log('Generated summary:', generateCandidateSummary(fullCandidateData));
      setSelectedCandidateDetails(fullCandidateData);
      setShowCVDetailsModal(true);
    } else {
      showToast('⚠️ Unable to load candidate details', 'error');
    }
  };

  const sendEmail = (candidate) => {
    // Generate email content
    const emailContent = {
      to: candidate.email,
      to_name: candidate.name,
      subject: `Job Opportunity - ${jobForm.title}`,
      body: `Dear ${candidate.name},

We are pleased to inform you that your application for the ${jobForm.title} position has been shortlisted.

We would like to schedule an interview with you to discuss this opportunity further.

Best regards,
HR Team`
    };

    setEmailToSend(emailContent);
    setShowEmailPreviewModal(true);
  };

  const confirmSendEmail = () => {
    if (!emailToSend) return;

    const subject = encodeURIComponent(emailToSend.subject);
    const body = encodeURIComponent(emailToSend.body);

    window.open(`mailto:${emailToSend.to}?subject=${subject}&body=${body}`, '_blank');

    setShowEmailPreviewModal(false);
    setEmailToSend(null);
    showToast('✉️ Email client opened successfully!', 'success');
  };

  const startOver = () => {
    setConfirmDialog({
      show: true,
      title: 'Start New Analysis?',
      message: 'Are you sure you want to start a new analysis? This will clear all current results and uploaded files.',
      type: 'warning',
      onConfirm: () => {
        setUploadedFiles([]);
        setAnalysisResults([]);
        setCandidates({ total: 0, shortlisted: 0, rejected: 0 });
        setJobForm({ title: '', requirements: '' });
        goToStep(1);
        showToast('✨ Ready for new CV analysis!', 'success');
        setConfirmDialog({ ...confirmDialog, show: false });
      }
    });
  };

  return (
    <div>
      <section className="dashboard-header">
        <div className="container">
          <h1>HR Dashboard</h1>
          <p>Upload CVs first, then define your job requirements to find the perfect candidates</p>
        </div>
      </section>

      <main className="container">
        {/* Settings Configuration Notification */}
        <SettingsNotification />

        {/* Progress Stepper */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '1rem',
          padding: '2rem 0',
          position: 'sticky',
          top: '80px',
          background: 'var(--background)',
          zIndex: 50,
          marginBottom: '2rem',
          borderBottom: '1px solid var(--border)'
        }}>
          {[
            { num: 1, label: 'Upload CVs', icon: '📋' },
            { num: 2, label: 'Job Requirements', icon: '📝' },
            { num: 3, label: 'Results', icon: '📊' }
          ].map((step, index) => (
            <React.Fragment key={step.num}>
              <div
                onClick={() => {
                  // Allow navigation to previous steps
                  if (step.num < currentStep || (step.num === 2 && uploadedFiles.length > 0)) {
                    goToStep(step.num);
                  }
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '12px',
                  background: currentStep === step.num ? 'var(--surface)' :
                             currentStep > step.num ? 'var(--surface-light)' :
                             'transparent',
                  border: `2px solid ${currentStep >= step.num ? 'var(--primary)' : 'var(--border)'}`,
                  cursor: (step.num < currentStep || (step.num === 2 && uploadedFiles.length > 0)) ? 'pointer' : 'default',
                  transition: 'all 0.3s ease',
                  opacity: currentStep >= step.num ? 1 : 0.5
                }}
                onMouseOver={(e) => {
                  if (step.num < currentStep || (step.num === 2 && uploadedFiles.length > 0)) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.2)';
                  }
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  background: currentStep === step.num ? 'linear-gradient(135deg, var(--primary), var(--secondary))' :
                             currentStep > step.num ? 'var(--success)' :
                             'var(--surface-light)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.1rem',
                  fontWeight: '700',
                  color: 'white',
                  transition: 'all 0.3s ease'
                }}>
                  {currentStep > step.num ? '✓' : step.icon}
                </div>
                <div>
                  <div style={{
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    fontWeight: '500',
                    marginBottom: '2px'
                  }}>
                    Step {step.num}
                  </div>
                  <div style={{
                    fontSize: '0.9rem',
                    fontWeight: '600',
                    color: currentStep >= step.num ? 'var(--text-primary)' : 'var(--text-muted)'
                  }}>
                    {step.label}
                  </div>
                </div>
              </div>
              {index < 2 && (
                <div style={{
                  width: '60px',
                  height: '2px',
                  background: currentStep > step.num ? 'var(--primary)' : 'var(--border)',
                  transition: 'background 0.3s ease'
                }}></div>
              )}
            </React.Fragment>
          ))}
        </div>

        <div className="dashboard-workflow">

          {/* Step 1: CV Upload Section */}
          <div className={`workflow-step ${currentStep === 1 ? 'active' : ''}`} id="step1">
            <div className="step-header">
              <div className="step-number">1</div>
              <div>
                <h2 className="step-title">Upload CVs</h2>
                <p className="step-description">Start by uploading all the CV files you want to analyze</p>
              </div>
            </div>

            <div className="upload-section animate-on-scroll">
              <div className="upload-area" onClick={uploadCVs}>
                <div className="upload-icon">📋</div>
                <p style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Drag and drop CV files here or click to browse</p>
                <button className="upload-btn" type="button">Choose Files</button>
                <p style={{ marginTop: '1rem' }}>
                  <small style={{ color: 'var(--text-muted)' }}>Supported formats: PDF, DOC, DOCX</small>
                </p>
              </div>

              {uploadProgress.show && (
                <div style={{
                  display: 'block',
                  marginTop: '1.5rem',
                  padding: '1.5rem',
                  background: 'var(--surface)',
                  borderRadius: '12px',
                  border: '1px solid var(--border)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <div className="loading-spinner" style={{ width: '24px', height: '24px' }}></div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '600', marginBottom: '0.25rem', color: 'var(--text-primary)' }}>
                        {uploadProgress.value < 30 ? '📤 Uploading CVs...' :
                         uploadProgress.value < 70 ? '🔍 Analyzing candidates...' :
                         uploadProgress.value < 100 ? '⚡ Matching skills and requirements...' :
                         '✓ Complete!'}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        {uploadProgress.value < 100 ? `Processing ${uploadedFiles.length} file${uploadedFiles.length > 1 ? 's' : ''}...` : 'Analysis finished successfully'}
                      </div>
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)', minWidth: '60px', textAlign: 'right' }}>
                      {uploadProgress.value}%
                    </div>
                  </div>
                  <div className="progress-bar" style={{
                    width: '100%',
                    height: '8px',
                    background: 'var(--surface-light)',
                    borderRadius: '999px',
                    overflow: 'hidden',
                    position: 'relative'
                  }}>
                    <div
                      className="progress-fill"
                      style={{
                        width: `${uploadProgress.value}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, var(--primary), var(--secondary))',
                        borderRadius: '999px',
                        transition: 'width 0.5s ease',
                        position: 'relative',
                        overflow: 'hidden'
                      }}
                    >
                      <div style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                        animation: 'shimmer 1.5s infinite'
                      }}></div>
                    </div>
                  </div>
                </div>
              )}

              {uploadedFiles.length > 0 && (
                <div style={{ display: 'block', marginTop: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', gap: '1rem' }}>
                    <h3 style={{ margin: 0 }}>Uploaded Files ({uploadedFiles.length})</h3>
                    <button
                      className="clear-all-btn"
                      onClick={() => {
                        setConfirmDialog({
                          show: true,
                          title: 'Remove All Files?',
                          message: `Are you sure you want to remove all ${uploadedFiles.length} uploaded files?`,
                          type: 'danger',
                          onConfirm: () => {
                            setUploadedFiles([]);
                            showToast('✓ All files removed', 'success');
                            setConfirmDialog({ ...confirmDialog, show: false });
                          }
                        });
                      }}
                      style={{
                        padding: '0.5rem 1rem',
                        background: 'transparent',
                        border: '1px solid var(--danger)',
                        color: 'var(--danger)',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: '500',
                        transition: 'all 0.3s ease'
                      }}
                      onMouseOver={(e) => {
                        e.target.style.background = 'var(--danger)';
                        e.target.style.color = 'white';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.background = 'transparent';
                        e.target.style.color = 'var(--danger)';
                      }}
                    >
                      Clear All
                    </button>
                  </div>
                  {currentStep === 1 && (
                    <div style={{
                      background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                      padding: '1rem 1.5rem',
                      borderRadius: '12px',
                      marginBottom: '1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)'
                    }}>
                      <div style={{ color: 'white' }}>
                        <div style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.25rem' }}>
                          ✓ {uploadedFiles.length} CV{uploadedFiles.length > 1 ? 's' : ''} Ready
                        </div>
                        <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>
                          Continue to define job requirements
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          goToStep(2);
                          showToast('📝 Now define your job requirements', 'info');
                        }}
                        style={{
                          padding: '0.75rem 2rem',
                          background: 'white',
                          color: 'var(--primary)',
                          border: 'none',
                          borderRadius: '8px',
                          fontSize: '1rem',
                          fontWeight: '700',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          whiteSpace: 'nowrap',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }}
                        onMouseOver={(e) => {
                          e.target.style.transform = 'translateX(4px) scale(1.05)';
                          e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                        }}
                        onMouseOut={(e) => {
                          e.target.style.transform = 'translateX(0) scale(1)';
                          e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                        }}
                      >
                        Next Step
                        <span style={{ fontSize: '1.3rem' }}>→</span>
                      </button>
                    </div>
                  )}
                  <div className="files-list" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="file-item">
                        <div className="file-info">
                          <div className="file-name">{file.name}</div>
                          <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                        </div>
                        <button className="remove-file" onClick={() => {
                          setUploadedFiles(prev => prev.filter((_, i) => i !== index));
                          showToast(`Removed ${file.name}`, 'info');
                        }}>
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>

          {/* Step 2: Job Requirements Section */}
          <div className={`workflow-step ${currentStep === 2 ? 'active' : ''}`} id="step2">
            <div className="step-header">
              <div className="step-number">2</div>
              <div>
                <h2 className="step-title">Define Job Requirements</h2>
                <p className="step-description">Enter your job requirements in natural language to match against the uploaded CVs</p>
              </div>
            </div>

            <div className="job-criteria animate-on-scroll">
              <form onSubmit={processAndAnalyze}>
                <div className="form-group">
                  <label htmlFor="jobTitle">Job Title/Role *</label>
                  <input
                    type="text"
                    id="jobTitle"
                    value={jobForm.title}
                    onChange={(e) => setJobForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Senior Software Developer"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="jobRequirements">
                    Job Requirements & Description *
                    <span style={{ float: 'right', fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>
                      {jobForm.requirements.length} characters
                    </span>
                  </label>
                  <textarea
                    id="jobRequirements"
                    value={jobForm.requirements}
                    onChange={(e) => setJobForm(prev => ({ ...prev, requirements: e.target.value }))}
                    style={{ minHeight: '200px', resize: 'vertical' }}
                    placeholder="Example: Looking for a Senior Software Developer with 5+ years of experience in React, Node.js, and TypeScript. Must have experience with cloud platforms (AWS/Azure), RESTful APIs, and agile methodologies. Strong problem-solving skills and ability to mentor junior developers preferred."
                    required
                  />
                  <small style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem', display: 'block' }}>
                    💡 Tip: Be specific about required skills, experience level, and key responsibilities for better matching results
                  </small>
                </div>

                <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                  <button
                    type="button"
                    onClick={() => goToStep(1)}
                    style={{
                      padding: '0.875rem 1.5rem',
                      background: 'transparent',
                      border: '2px solid var(--border)',
                      color: 'var(--text-primary)',
                      borderRadius: '10px',
                      fontSize: '0.95rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.borderColor = 'var(--primary)';
                      e.target.style.color = 'var(--primary)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.borderColor = 'var(--border)';
                      e.target.style.color = 'var(--text-primary)';
                    }}
                  >
                    <span style={{ fontSize: '1.2rem' }}>←</span>
                    Back to Upload
                  </button>
                  <button
                    type="submit"
                    className="analyze-btn"
                    style={{
                      flex: 1,
                      padding: '0.875rem 2rem',
                      background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                      color: 'white',
                      border: 'none',
                      borderRadius: '10px',
                      fontSize: '0.95rem',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 10px 25px -5px rgba(99, 102, 241, 0.4)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    🔍 Analyze CVs & Find Best Matches
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Step 3: Results Section */}
          <div className={`workflow-step ${currentStep === 3 ? 'active' : ''}`} id="step3">
            <div className="step-header">
              <div className="step-number">3</div>
              <div>
                <h2 className="step-title">Analysis Results</h2>
                <p className="step-description">View your matched candidates organized by suitability</p>
              </div>
            </div>

            <div className="candidates-overview">
              <div className="candidate-card total animate-on-scroll" onClick={() => showCandidates('total')}>
                <div className="candidate-count total">{candidates.total}</div>
                <div className="candidate-label">Total Candidates</div>
              </div>

              <div className="candidate-card shortlisted animate-on-scroll" onClick={() => showCandidates('shortlisted')}>
                <div className="candidate-count shortlisted">{candidates.shortlisted}</div>
                <div className="candidate-label">Shortlisted Candidates</div>
              </div>

              <div className="candidate-card rejected animate-on-scroll" onClick={() => showCandidates('rejected')}>
                <div className="candidate-count rejected">{candidates.rejected}</div>
                <div className="candidate-label">Rejected Candidates</div>
              </div>
            </div>

            {/* Start Over Button */}
            {candidates.total > 0 && (
              <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                <button
                  onClick={startOver}
                  style={{
                    padding: '1rem 2.5rem',
                    background: 'linear-gradient(135deg, #10b981, #059669)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 8px 20px rgba(16, 185, 129, 0.4)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 15px rgba(16, 185, 129, 0.3)';
                  }}
                >
                  <span style={{ fontSize: '1.2rem' }}>🔄</span>
                  Start New Analysis
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Candidates Modal */}
      {showCandidatesModal && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowCandidatesModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{modalData.status} Candidates ({modalData.candidates.length})</h2>
              <span className="close" onClick={() => setShowCandidatesModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <table className="candidate-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Match %</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {modalData.candidates.length === 0 ? (
                    <tr>
                      <td colSpan={4} style={{ textAlign: 'center', padding: '3rem' }}>
                        <div style={{ fontSize: '48px', marginBottom: '1rem', opacity: 0.5 }}>📭</div>
                        <div style={{ fontSize: '1.2rem', fontWeight: '600', marginBottom: '0.5rem' }}>No Candidates Found</div>
                        <div style={{ color: 'var(--text-muted)' }}>No candidates match this criteria yet.</div>
                      </td>
                    </tr>
                  ) : (
                    modalData.candidates.map(candidate => (
                      <React.Fragment key={candidate.id}>
                        <tr>
                          <td style={{ fontWeight: '600' }}>{candidate.name}</td>
                          <td>{candidate.email}</td>
                          <td><span className="match-percentage">{Math.round(candidate.match_score)}%</span></td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'column' }}>
                              <button
                                className="action-btn"
                                onClick={() => viewCandidateDetails(candidate)}
                                style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                              >
                                📋 View Details
                              </button>
                              {modalData.status === 'Shortlisted' && (
                                <button
                                  className="action-btn primary"
                                  onClick={() => openInterviewModal(candidate)}
                                  style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
                                >
                                  📅 Schedule Interview
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td colSpan={4} style={{ padding: '1rem', background: 'var(--surface-light)', borderBottom: '2px solid var(--border)' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                              {/* AI Analysis Section */}
                              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                                <span style={{ fontSize: '1.25rem', flexShrink: 0 }}>🤖</span>
                                <div style={{ flex: 1 }}>
                                  <div style={{
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    color: 'var(--primary)',
                                    marginBottom: '0.35rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px'
                                  }}>
                                    AI Analysis
                                  </div>
                                  <div style={{ fontSize: '0.9rem', lineHeight: '1.6', color: 'var(--text-secondary)' }}>
                                    {candidate.summary}
                                  </div>
                                </div>
                              </div>

                              {/* Actual Candidate Data from Full Details */}
                              {(() => {
                                const fullData = analysisResults.find(r => r.id === candidate.id);
                                if (!fullData) return null;

                                const hasMeaningfulData =
                                  (fullData.work_experience && fullData.work_experience.length > 0) ||
                                  (fullData.skills && fullData.skills.length > 0) ||
                                  (fullData.education && fullData.education.length > 0);

                                if (!hasMeaningfulData) return null;

                                return (
                                  <div style={{
                                    borderTop: '1px dashed var(--border)',
                                    paddingTop: '0.75rem',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '0.5rem'
                                  }}>
                                    {/* Work Experience */}
                                    {fullData.work_experience && fullData.work_experience.length > 0 && (
                                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                                        <span style={{ fontSize: '1rem', flexShrink: 0, marginTop: '0.1rem' }}>💼</span>
                                        <div style={{ flex: 1 }}>
                                          <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>Experience: </strong>
                                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                            {fullData.work_experience[0].title || fullData.work_experience[0].position} at {fullData.work_experience[0].company}
                                            {fullData.work_experience.length > 1 && ` (+${fullData.work_experience.length - 1} more)`}
                                          </span>
                                        </div>
                                      </div>
                                    )}

                                    {/* Skills */}
                                    {fullData.skills && fullData.skills.length > 0 && (
                                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                                        <span style={{ fontSize: '1rem', flexShrink: 0, marginTop: '0.1rem' }}>⚡</span>
                                        <div style={{ flex: 1 }}>
                                          <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>Skills: </strong>
                                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                            {fullData.skills.slice(0, 6).map(s => typeof s === 'string' ? s : s.name || s.skill).filter(Boolean).join(', ')}
                                            {fullData.skills.length > 6 && ` (+${fullData.skills.length - 6} more)`}
                                          </span>
                                        </div>
                                      </div>
                                    )}

                                    {/* Education */}
                                    {fullData.education && fullData.education.length > 0 && (
                                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                                        <span style={{ fontSize: '1rem', flexShrink: 0, marginTop: '0.1rem' }}>🎓</span>
                                        <div style={{ flex: 1 }}>
                                          <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>Education: </strong>
                                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                            {fullData.education[0].degree || fullData.education[0].qualification}
                                            {fullData.education[0].field && ` in ${fullData.education[0].field}`}
                                            {fullData.education[0].institution && ` from ${fullData.education[0].institution}`}
                                          </span>
                                        </div>
                                      </div>
                                    )}

                                    {/* Disclaimer */}
                                    <div style={{
                                      fontSize: '0.75rem',
                                      color: 'var(--text-muted)',
                                      fontStyle: 'italic',
                                      marginTop: '0.25rem',
                                      display: 'flex',
                                      alignItems: 'center',
                                      gap: '0.5rem'
                                    }}>
                                      <span>ℹ️</span>
                                      <span>AI analysis may not reflect complete candidate profile. Review full details before decision.</span>
                                    </div>
                                  </div>
                                );
                              })()}
                            </div>
                          </td>
                        </tr>
                      </React.Fragment>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Interview Scheduling Modal */}
      {showInterviewModal && selectedCandidate && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowInterviewModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Schedule Interview</h2>
              <span className="close" onClick={() => setShowInterviewModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <form onSubmit={scheduleInterview}>
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label htmlFor="candidateName" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Candidate:</label>
                  <input
                    type="text"
                    id="candidateName"
                    value={selectedCandidate.name}
                    readOnly
                    style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--surface-light)' }}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label htmlFor="candidateEmail" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Email:</label>
                  <input
                    type="email"
                    id="candidateEmail"
                    value={selectedCandidate.email}
                    readOnly
                    style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--surface-light)' }}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label htmlFor="interviewDateTime" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Interview Date & Time:</label>
                  <input
                    type="datetime-local"
                    id="interviewDateTime"
                    value={interviewForm.datetime}
                    onChange={(e) => {
                      const newForm = { ...interviewForm, datetime: e.target.value };
                      setInterviewForm(newForm);
                      if (selectedCandidate) generateEmailPreview(selectedCandidate, newForm);
                    }}
                    required
                    style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--background)' }}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label htmlFor="interviewType" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Interview Type:</label>
                  <select
                    id="interviewType"
                    value={interviewForm.type}
                    onChange={(e) => {
                      const newForm = { ...interviewForm, type: e.target.value };
                      setInterviewForm(newForm);
                      if (selectedCandidate) generateEmailPreview(selectedCandidate, newForm);
                    }}
                    style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--background)' }}
                  >
                    <option value="video">Video Call (Zoom, Teams, etc.)</option>
                    <option value="phone">Phone Call</option>
                    <option value="in-person">In-Person</option>
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                  <label htmlFor="interviewNotes" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Notes (Optional):</label>
                  <textarea
                    id="interviewNotes"
                    value={interviewForm.notes}
                    onChange={(e) => setInterviewForm(prev => ({ ...prev, notes: e.target.value }))}
                    placeholder="Any additional notes for the interview..."
                    style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--background)', minHeight: '80px', resize: 'vertical' }}
                  />
                </div>

                {emailPreview && (
                  <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'var(--surface-light)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: 'var(--primary)' }}>📧 Customize Email</h3>

                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                      <label htmlFor="emailSubject" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Subject:</label>
                      <input
                        type="text"
                        id="emailSubject"
                        value={emailPreview.subject}
                        onChange={(e) => setEmailPreview({ ...emailPreview, subject: e.target.value })}
                        style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--background)' }}
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="emailBody" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Message:</label>
                      <textarea
                        id="emailBody"
                        value={emailPreview.body}
                        onChange={(e) => setEmailPreview({ ...emailPreview, body: e.target.value })}
                        rows="8"
                        style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--background)', fontFamily: 'inherit', resize: 'vertical' }}
                      />
                    </div>

                    <small style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem', display: 'block' }}>
                      💡 You can edit the email content before sending
                    </small>
                  </div>
                )}

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => setShowInterviewModal(false)}
                    style={{ padding: '0.75rem 1.5rem', border: '1px solid var(--border)', borderRadius: '8px', backgroundColor: 'var(--surface)', color: 'var(--text-primary)', cursor: 'pointer' }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    style={{ padding: '0.75rem 1.5rem', border: 'none', borderRadius: '8px', backgroundColor: 'var(--primary)', color: 'white', cursor: 'pointer', fontWeight: '600' }}
                  >
                    Schedule Interview
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* CV Details Modal */}
      {showCVDetailsModal && selectedCandidateDetails && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowCVDetailsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h2>📋 Candidate Details</h2>
              <span className="close" onClick={() => setShowCVDetailsModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              {/* Candidate Header */}
              <div style={{ background: 'linear-gradient(135deg, var(--primary), var(--secondary))', padding: '1.5rem', borderRadius: '12px', marginBottom: '1.5rem', color: 'white' }}>
                <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.5rem' }}>{selectedCandidateDetails.name}</h2>
                <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.95rem' }}>
                  <div>📧 {selectedCandidateDetails.email}</div>
                  {selectedCandidateDetails.phone && <div>📞 {selectedCandidateDetails.phone}</div>}
                  <div style={{ background: 'rgba(255,255,255,0.2)', padding: '0.25rem 0.75rem', borderRadius: '20px', fontWeight: '600' }}>
                    Match: {Math.round(selectedCandidateDetails.match_score)}%
                  </div>
                </div>
              </div>

              {/* Education Section */}
              {selectedCandidateDetails.education && selectedCandidateDetails.education.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--primary)', borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem' }}>
                    🎓 Education
                  </h3>
                  {selectedCandidateDetails.education.map((edu, index) => (
                    <div key={index} style={{ marginBottom: '1rem', padding: '1rem', background: 'var(--surface-light)', borderRadius: '8px', borderLeft: '4px solid var(--primary)' }}>
                      <div style={{ fontWeight: '600', fontSize: '1.05rem', marginBottom: '0.25rem' }}>{edu.degree || edu.qualification}</div>
                      <div style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>{edu.institution || edu.school}</div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                        {edu.year || `${edu.start_year} - ${edu.end_year || 'Present'}`}
                        {edu.field && ` • ${edu.field}`}
                        {edu.gpa && ` • GPA: ${edu.gpa}`}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Work Experience Section */}
              {selectedCandidateDetails.work_experience && selectedCandidateDetails.work_experience.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--primary)', borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem' }}>
                    💼 Work Experience
                  </h3>
                  {selectedCandidateDetails.work_experience.map((work, index) => (
                    <div key={index} style={{ marginBottom: '1rem', padding: '1rem', background: 'var(--surface-light)', borderRadius: '8px', borderLeft: '4px solid var(--secondary)' }}>
                      <div style={{ fontWeight: '600', fontSize: '1.05rem', marginBottom: '0.25rem' }}>{work.title || work.position}</div>
                      <div style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>{work.company}</div>
                      <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                        {work.duration || `${work.start_date} - ${work.end_date || 'Present'}`}
                        {work.location && ` • ${work.location}`}
                      </div>
                      {work.responsibilities && work.responsibilities.length > 0 && (
                        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', fontSize: '0.9rem' }}>
                          {work.responsibilities.map((resp, idx) => (
                            <li key={idx} style={{ marginBottom: '0.25rem' }}>{resp}</li>
                          ))}
                        </ul>
                      )}
                      {work.description && (
                        <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', lineHeight: '1.5' }}>{work.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Skills Section */}
              {selectedCandidateDetails.skills && selectedCandidateDetails.skills.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--primary)', borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem' }}>
                    ⚡ Skills
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {selectedCandidateDetails.skills.map((skill, index) => (
                      <span key={index} style={{
                        background: 'var(--primary)',
                        color: 'white',
                        padding: '0.4rem 0.8rem',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        fontWeight: '500'
                      }}>
                        {typeof skill === 'string' ? skill : skill.name || skill.skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications/Achievements Section */}
              {selectedCandidateDetails.certifications && selectedCandidateDetails.certifications.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--primary)', borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem' }}>
                    🏆 Certifications & Achievements
                  </h3>
                  <div style={{ display: 'grid', gap: '0.75rem' }}>
                    {selectedCandidateDetails.certifications.map((cert, index) => (
                      <div key={index} style={{ padding: '0.75rem 1rem', background: 'var(--surface-light)', borderRadius: '8px', fontSize: '0.95rem' }}>
                        <span style={{ fontWeight: '600' }}>{typeof cert === 'string' ? cert : cert.name}</span>
                        {cert.issuer && <span style={{ color: 'var(--text-muted)' }}> • {cert.issuer}</span>}
                        {cert.date && <span style={{ color: 'var(--text-muted)' }}> • {cert.date}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Analysis Summary */}
              {(selectedCandidateDetails.strengths || selectedCandidateDetails.concerns || selectedCandidateDetails.summary) && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--primary)', borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem' }}>
                    🤖 AI Analysis
                  </h3>

                  {selectedCandidateDetails.summary && (
                    <p style={{ lineHeight: '1.6', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                      {selectedCandidateDetails.summary}
                    </p>
                  )}

                  {selectedCandidateDetails.strengths && selectedCandidateDetails.strengths.length > 0 && (
                    <div style={{ marginBottom: '0.75rem' }}>
                      <strong style={{ color: 'var(--success)', fontSize: '0.95rem' }}>✓ Strengths:</strong>
                      <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem' }}>
                        {selectedCandidateDetails.strengths.map((strength, idx) => (
                          <li key={idx} style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selectedCandidateDetails.concerns && selectedCandidateDetails.concerns.length > 0 && (
                    <div style={{ marginBottom: '0.75rem' }}>
                      <strong style={{ color: 'var(--accent)', fontSize: '0.95rem' }}>⚠️ Considerations:</strong>
                      <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem' }}>
                        {selectedCandidateDetails.concerns.map((concern, idx) => (
                          <li key={idx} style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                            {concern}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div style={{
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    borderRadius: '8px',
                    padding: '0.75rem',
                    marginTop: '1rem',
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    gap: '0.5rem',
                    alignItems: 'flex-start'
                  }}>
                    <span style={{ flexShrink: 0 }}>ℹ️</span>
                    <span>
                      <strong>Note:</strong> This AI analysis is automated and may not capture all candidate qualifications.
                      Please review the complete profile information above for accurate assessment.
                    </span>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button
                  onClick={() => setShowCVDetailsModal(false)}
                  style={{ flex: 1, padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', background: 'transparent', cursor: 'pointer' }}
                >
                  Close
                </button>
                {selectedCandidateDetails.match_status === 'shortlisted' && (
                  <button
                    onClick={() => {
                      setShowCVDetailsModal(false);
                      const candidateForInterview = {
                        id: selectedCandidateDetails.id,
                        name: selectedCandidateDetails.name,
                        email: selectedCandidateDetails.email,
                        match_score: selectedCandidateDetails.match_score
                      };
                      openInterviewModal(candidateForInterview);
                    }}
                    style={{ flex: 1, padding: '0.75rem', border: 'none', borderRadius: '8px', background: 'var(--primary)', color: 'white', cursor: 'pointer', fontWeight: '600' }}
                  >
                    Schedule Interview
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Email Preview Modal */}
      {showEmailPreviewModal && emailToSend && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowEmailPreviewModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h2>📧 Email Preview</h2>
              <span className="close" onClick={() => setShowEmailPreviewModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <div style={{ background: 'var(--surface-light)', padding: '1.5rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', marginBottom: '0.5rem' }}>
                    <strong style={{ minWidth: '80px', color: 'var(--text-secondary)' }}>To:</strong>
                    <span>{emailToSend.to_name} ({emailToSend.to})</span>
                  </div>
                  <div style={{ display: 'flex' }}>
                    <strong style={{ minWidth: '80px', color: 'var(--text-secondary)' }}>Subject:</strong>
                    <span>{emailToSend.subject}</span>
                  </div>
                </div>
                <div>
                  <strong style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '0.75rem' }}>Message:</strong>
                  <pre style={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'inherit',
                    margin: 0,
                    lineHeight: '1.6',
                    background: 'white',
                    padding: '1rem',
                    borderRadius: '6px',
                    border: '1px solid var(--border)'
                  }}>
                    {emailToSend.body}
                  </pre>
                </div>
              </div>

              <div style={{ background: '#e3f2fd', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                <strong>ℹ️ Note:</strong> This will open your default email client with the message pre-filled. You can edit before sending.
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                  onClick={() => setShowEmailPreviewModal(false)}
                  style={{ flex: 1, padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '8px', background: 'transparent', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  onClick={confirmSendEmail}
                  style={{ flex: 1, padding: '0.75rem', border: 'none', borderRadius: '8px', background: 'var(--primary)', color: 'white', cursor: 'pointer', fontWeight: '600' }}
                >
                  Open Email Client
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
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog({ ...confirmDialog, show: false })}
      />
    </div>
  );
}

export default Dashboard;