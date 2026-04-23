import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const initWidget = () => {
  const container = document.createElement('div');
  container.id = 'campgpt-widget-container';
  document.body.appendChild(container);

  const shadowRoot = container.attachShadow({ mode: 'open' });
  const mountPoint = document.createElement('div');
  shadowRoot.appendChild(mountPoint);

  // Inject styles into shadow DOM
  const style = document.createElement('style');
  style.textContent = `
    :host {
      all: initial;
      font-family: system-ui, -apple-system, sans-serif;
    }
  `;
  shadowRoot.appendChild(style);

  const root = createRoot(mountPoint);
  root.render(<App />);
};

if (document.readyState === 'complete') {
  initWidget();
} else {
  window.addEventListener('load', initWidget);
}
