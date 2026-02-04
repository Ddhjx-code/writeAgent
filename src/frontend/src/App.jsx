import React, { useState } from 'react';
import StoryWorkspace from './components/StoryWorkspace';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, storyWorkspace, characterManagement, etc.

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo-container">
          <h1>AI 协同小说创作平台</h1>
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
            <div className="dashboard-cards">
              <div className="card story-overview">
                <h3>故事信息</h3>
                <p>当前项目：无</p>
                <p>总计字数：0字</p>
                <button className="primary-btn">开始新故事</button>
              </div>
              <div className="card ai-status">
                <h3>AI代理状态</h3>
                <p>活跃代理数：0/9</p>
                <p>运行状态：待机</p>
                <button className="secondary-btn">管理AI</button>
              </div>
              <div className="card recent-activity">
                <h3>最近活动</h3>
                <p>无近期活动</p>
              </div>
            </div>
          </div>
        )}
        {currentView === 'storyWorkspace' && <StoryWorkspace />}
        {currentView === 'characters' && <div className="characters-view">角色管理功能</div>}
        {currentView === 'settings' && <div className="settings-view">系统设置功能</div>}
      </main>
    </div>
  );
}

export default App;