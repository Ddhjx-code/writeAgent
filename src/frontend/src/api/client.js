import { useState, useEffect } from 'react';

// API客户端
class ApiClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API请求错误: ${endpoint}`, error);
      throw error;
    }
  }

  // 故事相关API
  async getSystemStatus() {
    return this.request('/api/status');
  }

  async createStory(config) {
    return this.request('/api/stories/create', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async getStory(storyId) {
    return this.request(`/api/stories/${storyId}`);
  }

  async startWriting(storyId) {
    return this.request(`/api/stories/${storyId}/start`, {
      method: 'POST',
    });
  }

  async getStoryProgress(storyId) {
    return this.request(`/api/stories/${storyId}/progress`);
  }

  async getAgentStatus() {
    return this.request('/api/agents/status');
  }
}

// API客户端实例
const api = new ApiClient();

// 导出API供组件使用
export default api;