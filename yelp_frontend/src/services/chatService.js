import api from './api.js';

export const sendMessageToAI = async (message, history) => {
  const response = await api.post('/ai-assistant/chat', {
    message: message,
    conversation_history: history
  });
  return response.data;
};

export const getChatHistory = async () => {
  const response = await api.get('/ai-assistant/history');
  return response.data;
};

export const clearChatHistory = async () => {
  return await api.delete('/ai-assistant/history');
};
