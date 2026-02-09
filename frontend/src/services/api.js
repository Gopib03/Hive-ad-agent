// src/services/api.js
// API Service for Backend Communication

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// System Status
export const getSystemStatus = async () => {
  try {
    const response = await api.get('/api/system/status');
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    return { 
      status: 'offline',
      agents: [],
      workflows_completed: 0 
    };
  }
};

// Execute Workflow
export const executeWorkflow = async (workflowType, data) => {
  try {
    const response = await api.post('/api/workflows/execute', {
      workflow_type: workflowType,
      data: data,
    });
    return response.data;
  } catch (error) {
    console.error('Workflow Error:', error);
    throw error;
  }
};

// Get AI Usage Stats
export const getAIUsageStats = async () => {
  try {
    const response = await api.get('/api/analytics/ai-usage');
    return response.data;
  } catch (error) {
    console.error('AI Stats Error:', error);
    return {
      total_requests: 0,
      total_tokens: 0,
      total_cost: 0
    };
  }
};

export default api;