import { useState, useEffect } from 'react';

// WebSocket客户端
class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.listeners = [];
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WebSocket连接已建立');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach(callback => callback(data));
      } catch (error) {
        console.error('WebSocket消息解析错误:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket连接已断开');
      // 尝试重新连接
      setTimeout(() => {
        console.log('尝试重新连接WebSocket...');
        this.connect();
      }, 3000);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// 故事更新WebSocket客户端
const storyUpdatesSocket = new WebSocketClient('ws://localhost:8000/ws/updates');
storyUpdatesSocket.connect();

// 代理消息WebSocket客户端
const agentMessagesSocket = new WebSocketClient('ws://localhost:8000/ws/agent-messages');
agentMessagesSocket.connect();

// 导出WebSocket客户端
export { storyUpdatesSocket, agentMessagesSocket };