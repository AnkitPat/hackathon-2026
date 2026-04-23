const API_URL = 'http://localhost:8000/chat'; // Default to local for now

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const getSessionId = (): string => {
  let sessionId = localStorage.getItem('campgpt_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('campgpt_session_id', sessionId);
  }
  return sessionId;
};

export const sendMessage = async (message: string): Promise<string> => {
  const sessionId = getSessionId();
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok) throw new Error('Failed to send message');
  const data = await response.json();
  return data.response;
};
