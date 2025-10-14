import React, { useState, useEffect } from 'react';
import { useHeaderScroll } from '../hooks/useHeaderScroll';
import { useScrollAnimations } from '../hooks/useScrollAnimations';
import { useToast } from '../contexts/ToastContext';
import ConfirmDialog from '../components/ConfirmDialog';

function Calendar() {
  const { showToast } = useToast();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [interviews, setInterviews] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [loadingInterviews, setLoadingInterviews] = useState(true);
  const [showAllInterviewsModal, setShowAllInterviewsModal] = useState(false);
  const [selectedDayInterviews, setSelectedDayInterviews] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    title: '',
    message: '',
    type: 'warning',
    onConfirm: null
  });

  // Use custom hooks
  useHeaderScroll();
  useScrollAnimations();

  useEffect(() => {
    loadInterviews();
  }, []);

  useEffect(() => {
    updateCurrentMonth();
  }, [currentDate]);

  const loadInterviews = async () => {
    setLoadingInterviews(true);
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/api/v1/interviews/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        // Handle both direct array and paginated response
        const interviewsList = data.interviews || data;

        // Transform backend data to match calendar format
        const transformedInterviews = interviewsList.map(interview => ({
          id: interview.id,
          candidate_name: interview.candidate?.name || 'Unknown',
          candidate_email: interview.candidate?.email || '',
          job_title: interview.position || interview.job_posting?.title || 'Position',
          date: new Date(interview.scheduled_datetime),
          scheduled_datetime: interview.scheduled_datetime,
          interview_type: interview.interview_type || 'video',
          status: interview.status || 'Scheduled',
          notes: interview.notes || ''
        }));
        setInterviews(transformedInterviews);
      } else if (response.status === 401) {
        // Token expired, redirect to login
        window.location.href = '/login';
      } else {
        console.error('Failed to load interviews');
        setInterviews([]);
      }
    } catch (error) {
      console.error('Error loading interviews:', error);
      setInterviews([]);
    } finally {
      setLoadingInterviews(false);
    }
  };

  const updateCurrentMonth = () => {
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
  };

  const previousMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() - 1);
    setCurrentDate(newDate);
  };

  const nextMonth = () => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + 1);
    setCurrentDate(newDate);
  };

  const getDaysInMonth = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const days = [];
    for (let i = 0; i < 42; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      days.push(date);
    }
    return days;
  };

  const isToday = (date) => {
    const today = new Date();
    return isSameDay(date, today);
  };

  const isSameDay = (date1, date2) => {
    return date1.getDate() === date2.getDate() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getFullYear() === date2.getFullYear();
  };

  const getInterviewsForDay = (date) => {
    return interviews.filter(interview => isSameDay(interview.date, date));
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDateTimeLocal = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const openInterviewModal = (interview) => {
    setSelectedInterview(interview);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedInterview(null);
  };

  const saveInterview = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/interviews/${selectedInterview.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          scheduled_datetime: formData.get('interviewDateTime'),
          interview_type: formData.get('interviewType'),
          notes: formData.get('interviewNotes')
        })
      });

      if (response.ok) {
        showToast('✓ Interview updated successfully!', 'success');
        closeModal();
        loadInterviews(); // Reload interviews
      } else if (response.status === 401) {
        window.location.href = '/login';
      } else {
        showToast('❌ Failed to update interview. Please try again.', 'error');
      }
    } catch (error) {
      console.error('Error updating interview:', error);
      showToast('❌ Failed to update interview. Please try again.', 'error');
    }
  };

  const cancelInterview = (interviewId) => {
    setConfirmDialog({
      show: true,
      title: 'Cancel Interview?',
      message: 'Are you sure you want to cancel this interview? This action cannot be undone.',
      type: 'danger',
      onConfirm: async () => {
        setConfirmDialog({ ...confirmDialog, show: false });
        try {
          const token = localStorage.getItem('auth_token');
          const response = await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            showToast('✓ Interview cancelled successfully!', 'success');
            loadInterviews(); // Reload interviews
          } else if (response.status === 401) {
            window.location.href = '/login';
          } else {
            showToast('❌ Failed to cancel interview. Please try again.', 'error');
          }
        } catch (error) {
          console.error('Error cancelling interview:', error);
          showToast('❌ Failed to cancel interview. Please try again.', 'error');
        }
      }
    });
  };

  const getUpcomingInterviews = () => {
    const now = new Date();

    // Only show future interviews (original logic)
    return interviews
      .filter(interview => interview.date >= now)
      .sort((a, b) => a.date - b.date)
      .slice(0, 6);
  };

  const openAllInterviewsModal = (date, interviews) => {
    setSelectedDate(date);
    setSelectedDayInterviews(interviews);
    setShowAllInterviewsModal(true);
  };

  return (
    <div>
      <section className="calendar-header">
        <div className="container">
          <h1>Interview Calendar</h1>
          <p>View and manage all scheduled interviews in one place</p>
        </div>
      </section>

      <main className="container">
        <div className="calendar-controls animate-on-scroll">
          <div className="calendar-nav">
            <button className="nav-btn" onClick={previousMonth}>‹ Previous</button>
            <div className="current-month">{updateCurrentMonth()}</div>
            <button className="nav-btn" onClick={nextMonth}>Next ›</button>
          </div>
          <button
            className="nav-btn"
            onClick={loadInterviews}
            style={{
              background: 'var(--primary)',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            🔄 Refresh
          </button>
        </div>

        <div className="calendar-container animate-on-scroll animate-delay-1">
          <div className="calendar-grid">
            {/* Calendar Headers */}
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="calendar-day-header">{day}</div>
            ))}

            {/* Calendar Days */}
            {getDaysInMonth().map((date, index) => {
              const dayInterviews = getInterviewsForDay(date);
              const isCurrentMonth = date.getMonth() === currentDate.getMonth();
              const visibleInterviews = dayInterviews.slice(0, 5);
              const hiddenCount = Math.max(0, dayInterviews.length - 5);

              return (
                <div
                  key={index}
                  className={`calendar-day ${
                    !isCurrentMonth ? 'other-month' : ''
                  } ${isToday(date) ? 'today' : ''}`}
                >
                  <span className="day-number">{date.getDate()}</span>

                  {visibleInterviews.map(interview => {
                    const isPast = interview.date < new Date();
                    return (
                      <div
                        key={interview.id}
                        className="interview-event"
                        onClick={(e) => {
                          e.stopPropagation();
                          openInterviewModal(interview);
                        }}
                        style={{
                          background: isPast ? '#6b7280' : 'var(--primary)',
                          opacity: isPast ? 0.6 : 1,
                          textDecoration: isPast ? 'line-through' : 'none'
                        }}
                        title={isPast ? 'Past Interview' : ''}
                      >
                        <div>{interview.candidate_name}</div>
                        <div className="interview-time">
                          {formatTime(interview.date)}
                          {isPast && <span style={{ fontSize: '0.7rem', marginLeft: '4px' }}>✓</span>}
                        </div>
                      </div>
                    );
                  })}

                  {hiddenCount > 0 && (
                    <div
                      className="interview-event"
                      onClick={(e) => {
                        e.stopPropagation();
                        openAllInterviewsModal(date, dayInterviews);
                      }}
                      style={{
                        background: 'var(--primary)',
                        color: 'white',
                        textAlign: 'center',
                        fontWeight: '600',
                        cursor: 'pointer',
                        fontSize: '0.85rem'
                      }}
                    >
                      +{hiddenCount} more
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="upcoming-interviews animate-on-scroll animate-delay-2">
          <h2>Upcoming Interviews</h2>
          <div className="interview-list" id="interviewList">
            {getUpcomingInterviews().length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                No upcoming interviews scheduled.
              </p>
            ) : (
              getUpcomingInterviews().map(interview => {
                const date = interview.date;
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

                return (
                  <div key={interview.id} className="interview-card">
                    <div className="interview-date">
                      <div className="day">{date.getDate()}</div>
                      <div className="month">{monthNames[date.getMonth()]}</div>
                    </div>
                    <div className="interview-details">
                      <h3>{interview.candidate_name}</h3>
                      <p><strong>Applying For:</strong> {interview.job_title}</p>
                      <p><strong>Email:</strong> {interview.candidate_email}</p>
                      <p><strong>Time:</strong> {formatTime(date)}</p>
                      <p><strong>Type:</strong> {interview.interview_type || 'Video'}</p>
                      <p><strong>Status:</strong> {interview.status || 'Scheduled'}</p>
                    </div>
                    <div className="interview-actions">
                      <button
                        className="action-btn reschedule-btn"
                        onClick={() => openInterviewModal(interview)}
                      >
                        Reschedule
                      </button>
                      <button
                        className="action-btn cancel-btn"
                        onClick={() => cancelInterview(interview.id)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </main>

      {/* Interview Details Modal */}
      {showModal && selectedInterview && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content">
            <div className="modal-header">
              <h2>Interview Details</h2>
              <span className="close" onClick={closeModal}>&times;</span>
            </div>
            <div className="modal-body">
              <form onSubmit={saveInterview}>
                <input type="hidden" name="interviewId" value={selectedInterview.id} />

                <div className="form-group">
                  <label>Candidate Name:</label>
                  <input type="text" name="candidateName" value={selectedInterview.candidate_name} readOnly />
                </div>

                <div className="form-group">
                  <label>Email:</label>
                  <input type="email" name="candidateEmail" value={selectedInterview.candidate_email} readOnly />
                </div>

                <div className="form-group">
                  <label>Job Title:</label>
                  <input type="text" name="position" value={selectedInterview.job_title} readOnly />
                </div>

                <div className="form-group">
                  <label>Interview Date & Time:</label>
                  <input
                    type="datetime-local"
                    name="interviewDateTime"
                    defaultValue={formatDateTimeLocal(selectedInterview.date)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Interview Type:</label>
                  <select name="interviewType" defaultValue={selectedInterview.interview_type}>
                    <option value="video">Video Call</option>
                    <option value="phone">Phone Call</option>
                    <option value="in-person">In Person</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Notes:</label>
                  <textarea
                    name="interviewNotes"
                    rows="4"
                    defaultValue={selectedInterview.notes || ''}
                    placeholder="Add any notes about the interview..."
                  ></textarea>
                </div>

                <div className="modal-actions">
                  <button type="submit" className="save-btn">Save Changes</button>
                  <button type="button" className="cancel-btn" onClick={closeModal}>Cancel</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* All Interviews Modal */}
      {showAllInterviewsModal && selectedDate && (
        <div className="modal" style={{ display: 'block' }} onClick={() => setShowAllInterviewsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', maxHeight: '80vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h2>All Interviews - {selectedDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</h2>
              <span className="close" onClick={() => setShowAllInterviewsModal(false)}>&times;</span>
            </div>
            <div className="modal-body">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {selectedDayInterviews.map(interview => (
                  <div
                    key={interview.id}
                    style={{
                      padding: '1rem',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      background: 'var(--surface-light)',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.background = 'var(--surface)';
                      e.currentTarget.style.borderColor = 'var(--primary)';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.background = 'var(--surface-light)';
                      e.currentTarget.style.borderColor = 'var(--border)';
                    }}
                  >
                    <h3 style={{ marginBottom: '0.5rem', fontSize: '1.1rem' }}>{interview.candidate_name}</h3>
                    <p style={{ marginBottom: '0.25rem' }}><strong>Time:</strong> {formatTime(interview.date)}</p>
                    <p style={{ marginBottom: '0.25rem' }}><strong>Job Title:</strong> {interview.job_title}</p>
                    <p style={{ marginBottom: '0.25rem' }}><strong>Type:</strong> {interview.interview_type || 'Video'}</p>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                      <button
                        className="action-btn reschedule-btn"
                        onClick={() => {
                          setShowAllInterviewsModal(false);
                          openInterviewModal(interview);
                        }}
                        style={{ flex: 1, padding: '0.5rem', fontSize: '0.9rem' }}
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
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
        confirmText="Cancel Interview"
        cancelText="Keep Interview"
        onConfirm={confirmDialog.onConfirm}
        onCancel={() => setConfirmDialog({ ...confirmDialog, show: false })}
      />
    </div>
  );
}

export default Calendar;