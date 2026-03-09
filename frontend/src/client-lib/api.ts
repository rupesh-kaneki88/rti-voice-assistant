import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session Management
export const createSession = async (language: string) => {
  const response = await api.post('/session/create', { language });
  return response.data;
};

export const getSession = async (sessionId: string) => {
  const response = await api.get(`/session/${sessionId}`);
  return response.data;
};

export const haveConversation = async (sessionId: string, message: string, language: string) => {
  const response = await api.post(`/session/${sessionId}/conversation`, {
    message,
    language,
  });
  return response.data;
};

// Voice Services
export const transcribeAudio = async (audioBase64: string, language: string) => {
  const response = await api.post('/voice/transcribe', {
    audio: audioBase64,
    language,
  });
  return response.data;
};

export const extractFormData = async (text: string, language: string) => {
  const response = await api.post('/voice/extract-form-data', null, {
    params: { text, language }
  });
  return response.data;
};

export const textToSpeech = async (text: string, language: string) => {
  const response = await api.post('/voice/tts', {
    text,
    language,
  });
  return response.data;
};

// Form Management
export const updateForm = async (sessionId: string, field: string, value: string) => {
  const response = await api.post(`/form/${sessionId}/update`, {
    field,
    value,
  });
  return response.data;
};

export const getForm = async (sessionId: string) => {
  const response = await api.get(`/form/${sessionId}`);
  return response.data;
};

export const generateDocument = async (sessionId: string) => {
  const response = await api.post(`/form/${sessionId}/generate`);
  return response.data;
};

// Legal Guidance
export const getRTIGuidance = async (language: string) => {
  const response = await api.post(`/guidance/explain?language=${language}`);
  return response.data;
};

export default api;
