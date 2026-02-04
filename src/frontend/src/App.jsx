import React, { useState, useEffect } from 'react';
import StoryWorkspace from './components/StoryWorkspace';
import api from './api/client';
import { storyUpdatesSocket } from './api/websocket';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, storyWorkspace, characterManagement, etc.
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取系统状态
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        setLoading(true);
        const response = await api.getSystemStatus();
        if (response.success) {
          setSystemStatus(response.data.status);
        } else {
          setError(response.error || '获取系统状态失败');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // 初始加载
    fetchSystemStatus();

    // 添加WebSocket监听器
    const handleStatusUpdate = (data) => {
      if (data.error) {
        setError(data.error);
      } else {
        setSystemStatus(data);
      }
    };

    storyUpdatesSocket.addListener(handleStatusUpdate);

    // 清理函数
    return () => {
      storyUpdatesSocket.removeListener(handleStatusUpdate);
    };
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo-container">
          <h1>AI 协同小说创作平台</h1>
        </div>
        <div className="status-indicator">
          <span className={`status ${systemStatus?.is_running ? 'running' : 'idle'}`}>
            {systemStatus ? '系统运行中' : loading ? '连接中...' : error ? '连接失败' : '未连接'}
          </span>
        </div>
        <nav className="main-nav">
          <button
            className={currentView === 'dashboard' ? 'active' : ''}
            onClick={() => setCurrentView('dashboard')}
          >
            概览
          </button>
          <button
            className={currentView === 'storyWorkspace' ? 'active' : ''}
            onClick={() => setCurrentView('storyWorkspace')}
          >
            创作工坊
          </button>
          <button
            className={currentView === 'characters' ? 'active' : ''}
            onClick={() => setCurrentView('characters')}
          >
            角色画廊
          </button>
          <button
            className={currentView === 'settings' ? 'active' : ''}
            onClick={() => setCurrentView('settings')}
          >
            系统设置
          </button>
        </nav>
      </header>

      <main className="app-main">
        {currentView === 'dashboard' && (
          <div className="dashboard">
            <h2>创作概览</h2>
            {error && (
              <div className="error-message">
                <p>错误: {error}</p>
              </div>
            )}
            <div className="dashboard-cards">
              <div className="card story-overview">
                <h3>故事信息</h3>
                <p>当前项目：{systemStatus?.current_story || '无'}</p>
                <p>系统状态：{systemStatus?.engine_state || '未知'}</p>
                <button className="primary-btn" onClick={() => setCurrentView('storyWorkspace')}>
                  开始新故事
                </button>
              </div>
              <div className="card ai-status">
                <h3>AI代理状态</h3>
                <p>活跃代理数：{systemStatus?.is_running ? '9/9' : '0/9'}</p>
                <p>运行状态：{systemStatus?.is_running ? '运行中' : '待机'}</p>
                <button className="secondary-btn">管理AI</button>
              </div>
              <div className="card recent-activity">
                <h3>最近活动</h3>
                <p>最后更新：{new Date().toLocaleString('zh-CN')}</p>
              </div>
            </div>
          </div>
        )}
        {currentView === 'storyWorkspace' && <StoryWorkspace />}
        {currentView === 'characters' && <div className="characters-view">角色管理功能</div>}
        {currentView === 'settings' &&
        <div className="settings-view">
          <h2>系统设置</h2>
          <div className="card">
            <h3>API服务状态</h3>
            <p>当前连接: {systemStatus ? '已连接到后端API' : '未连接'}</p>
            <p>系统状态: {systemStatus?.engine_state || '未知'}</p>
          </div>
        </div>}
      </main>
    </div>
  );
}

export default App;