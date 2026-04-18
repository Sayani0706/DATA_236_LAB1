import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api.js';
import { clearChatHistory } from '../../services/chatService.js';
import ThinkingIndicator from './ThinkingIndicator.js';
import RestaurantCard from '../Restaurant/RestaurantCard.js';

const ChatWindow = () => {
  const [messages, setMessages]     = useState([]);
  const [input, setInput]           = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [clearError, setClearError] = useState('');
  const bottomRef                   = useRef(null);
  const navigate                    = useNavigate();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  // Shared AI call used by both typed messages and quick buttons
  const callAI = async (text, currentMessages) => {
    const userMsg    = { role: 'user', content: text };
    const newHistory = [...currentMessages, userMsg];
    setMessages(newHistory);
    setInput('');
    setIsThinking(true);

    try {
      const response = await api.post('/ai-assistant/chat', {
        message:              text,
        conversation_history: currentMessages.map(m => ({ role: m.role, content: m.content })),
      });
      setMessages([...newHistory, {
        role:            'assistant',
        content:         response.data.response,
        recommendations: response.data.recommendations,
      }]);
    } catch (err) {
      setMessages([...newHistory, {
        role:    'assistant',
        content: 'Sorry, I couldn\'t connect to the server. Please make sure you are logged in.',
      }]);
    } finally {
      setIsThinking(false);
    }
  };

  const sendMessage = () => {
    if (!input.trim() || isThinking) return;
    callAI(input.trim(), messages);
  };

  const sendQuickMessage = (text) => {
    if (isThinking) return;
    callAI(text, messages);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    setClearError('');
    try {
      await clearChatHistory();
      setMessages([]);
    } catch (err) {
      setClearError('Could not clear chat history. Please try again.');
      setTimeout(() => setClearError(''), 3000);
    }
  };

  return (
    <div className="chat-window border rounded bg-white shadow-sm p-3">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <span className="fw-bold text-danger">🤖 AI Assistant</span>
        <button className="btn btn-sm btn-outline-secondary" onClick={clearChat}>
          Clear Chat
        </button>
      </div>

      {clearError && <div className="alert alert-warning py-1 mb-2 small">{clearError}</div>}

      {/* Quick action buttons */}
      <div className="mb-2 d-flex flex-wrap gap-1">
        {['Find dinner tonight', 'Best rated near me', 'Vegan options'].map(q => (
          <button
            key={q}
            className="btn btn-sm btn-outline-danger"
            onClick={() => sendQuickMessage(q)}
            disabled={isThinking}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Conversation history */}
      <div className="history mb-3" style={{ height: '400px', overflowY: 'auto' }}>
        {messages.length === 0 && (
          <p className="text-center text-muted mt-5">
            Ask me for a restaurant recommendation!
          </p>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`mb-3 ${m.role === 'user' ? 'text-end' : ''}`}>
            <div
              className={`d-inline-block p-2 rounded shadow-sm ${
                m.role === 'user' ? 'bg-danger text-white' : 'bg-light border'
              }`}
              style={{ maxWidth: '85%', textAlign: 'left' }}
            >
              {m.content}
            </div>

            {/* Clickable restaurant recommendation cards */}
            {m.recommendations && m.recommendations.length > 0 && (
              <div className="mt-2 row g-2 justify-content-start">
                {m.recommendations.map(res => (
                  <div
                    key={res.id}
                    className="col-12"
                    onClick={() => navigate(`/restaurants/${res.id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    <RestaurantCard restaurant={res} isCompact />
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {isThinking && <ThinkingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="input-group">
        <input
          className="form-control"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="e.g. I want something romantic tonight..."
          disabled={isThinking}
        />
        <button
          className="btn btn-danger"
          onClick={sendMessage}
          disabled={isThinking || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
