import React, { useState } from 'react';
import { ChatBubble } from './components/ChatBubble';
import { ChatWindow } from './components/ChatWindow';

const App = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <ChatBubble onClick={() => setIsOpen(true)} />
      {isOpen && <ChatWindow onClose={() => setIsOpen(false)} />}
    </>
  );
};

export default App;
