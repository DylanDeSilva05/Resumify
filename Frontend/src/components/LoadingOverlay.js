import React from 'react';

function LoadingOverlay({ message = "Loading..." }) {
  return (
    <div className="loading-overlay">
      <div className="loading-spinner-large"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
}

export default LoadingOverlay;
