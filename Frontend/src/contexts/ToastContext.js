import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'success', duration = null) => {
    const id = Date.now() + Math.random(); // More unique ID

    // Custom duration based on type
    let autoDismissTime = duration;
    if (!autoDismissTime) {
      switch (type) {
        case 'error':
          autoDismissTime = 5000; // Errors stay longer
          break;
        case 'warning':
          autoDismissTime = 4000;
          break;
        case 'info':
          autoDismissTime = 3500;
          break;
        case 'success':
        default:
          autoDismissTime = 3500; // Success messages stay longer
          break;
      }
    }

    const newToast = { id, message, type, duration: autoDismissTime };
    setToasts(prev => [...prev, newToast]);

    // Auto-remove after duration
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, autoDismissTime);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            toast={toast}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
};

// Individual Toast component with progress bar
const Toast = ({ toast, onClose }) => {
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 100 - (elapsed / toast.duration) * 100);
      setProgress(remaining);

      if (remaining === 0) {
        clearInterval(interval);
      }
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, [toast.duration]);

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'info':
        return 'ℹ';
      case 'warning':
        return '⚠';
      default:
        return 'ℹ';
    }
  };

  return (
    <div className={`toast toast-${toast.type}`}>
      <span className="toast-icon">{getIcon()}</span>
      <span className="toast-message">{toast.message}</span>
      <button
        className="toast-close"
        onClick={onClose}
        aria-label="Close notification"
      >
        ✕
      </button>
      <div
        className="toast-progress"
        style={{
          width: `${progress}%`,
          color: toast.type === 'success' ? '#10b981' :
                 toast.type === 'error' ? '#ef4444' :
                 toast.type === 'warning' ? '#f59e0b' : '#3b82f6'
        }}
      />
    </div>
  );
};
