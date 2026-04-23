import React from 'react';

interface Props {
  onClick: () => void;
}

export const ChatBubble = ({ onClick }: Props) => (
  <button 
    onClick={onClick}
    style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      width: '60px',
      height: '60px',
      borderRadius: '50%',
      backgroundColor: '#007bff',
      color: 'white',
      border: 'none',
      cursor: 'pointer',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      fontSize: '24px',
      zIndex: 9999
    }}
  >
    💬
  </button>
);
