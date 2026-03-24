import React from 'react';

const ThinkingIndicator = () => {
  return (
    <div className="d-flex align-items-center p-2 my-2 text-muted" style={{ fontStyle: 'italic' }}>
      <div className="spinner-border spinner-border-sm text-danger me-2" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      <span>AI Assistant is thinking...</span>
    </div>
  );
};

export default ThinkingIndicator;