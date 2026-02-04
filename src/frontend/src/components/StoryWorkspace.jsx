import React, { useState } from 'react';

const StoryWorkspace = () => {
  const [story, setStory] = useState({
    title: '',
    genre: '奇幻',
    description: '',
    targetLength: 10000,
    outline: '',
    chaptersCount: 10,
    povCharacter: '',
  });

  const [characters, setCharacters] = useState([]);
  const [characterInput, setCharacterInput] = useState({
    name: '',
    role: '主角',
    description: '',
  });

  const [currentChapter, setCurrentChapter] = useState('');
  const [storyProgress, setStoryProgress] = useState(0);
  const [agentStatus, setAgentStatus] = useState({
    isRunning: false,
    activeAgents: 0,
    message: '就绪',
  });

  const [feedback, setFeedback] = useState('');

  const handleStoryChange = (field, value) => {
    setStory(prev => ({ ...prev, [field]: value }));
  };

  const handleCharacterChange = (field, value) => {
    setCharacterInput(prev => ({ ...prev, [field]: value }));
  };

  const addCharacter = () => {
    if (characterInput.name) {
      setCharacters(prev => [...prev, { ...characterInput, id: Date.now() }]);
      setCharacterInput({ name: '', role: '主角', description: '' });
    }
  };

  const handleStartWriting = () => {
    setAgentStatus({
      isRunning: true,
      activeAgents: 9,
      message: 'AI代理商正在积极写作',
    });
    setStoryProgress(10);
  };

  const handleFeedback = () => {
    setAgentStatus({
      isRunning: true,
      activeAgents: 9,
      message: 'AI正在处理反馈...',
    });
  };

  return (
    <div className="story-workspace">
      <div className="story-workspace-content">
        <aside className="story-input-panel">
          <div className="input-section">
            <h3>故事信息</h3>
            <div className="form-group">
              <label>故事标题</label>
              <input
                type="text"
                value={story.title}
                onChange={(e) => handleStoryChange('title', e.target.value)}
                placeholder="输入故事标题..."
              />
            </div>
            <div className="form-group">
              <label>故事类型</label>
              <select
                value={story.genre}
                onChange={(e) => handleStoryChange('genre', e.target.value)}
              >
                <option value="奇幻">奇幻</option>
                <option value="科幻">科幻</option>
                <option value="悬疑">悬疑</option>
                <option value="爱情">爱情</option>
                <option value="惊悚">惊悚</option>
                <option value="文学小说">文学小说</option>
                <option value="历史">历史</option>
                <option value="恐怖">恐怖</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div className="form-group">
              <label>故事描述</label>
              <textarea
                value={story.description}
                onChange={(e) => handleStoryChange('description', e.target.value)}
                placeholder="简要描述您的故事..."
                rows={3}
              ></textarea>
            </div>
            <div className="form-group">
              <label>目标字数</label>
              <input
                type="range"
                min="1000"
                max="100000"
                step="1000"
                value={story.targetLength}
                onChange={(e) => handleStoryChange('targetLength', parseInt(e.target.value))}
              />
              <span className="slider-value">{story.targetLength.toLocaleString()} 字</span>
            </div>
          </div>

          <div className="input-section">
            <h3>故事大纲</h3>
            <div className="form-group">
              <label>大纲内容</label>
              <textarea
                value={story.outline}
                onChange={(e) => handleStoryChange('outline', e.target.value)}
                placeholder="提供详细的故事大纲，或留空让AI生成..."
                rows={5}
              ></textarea>
            </div>
            <div className="form-group">
              <label>章节数量</label>
              <input
                type="range"
                min="1"
                max="30"
                value={story.chaptersCount}
                onChange={(e) => handleStoryChange('chaptersCount', parseInt(e.target.value))}
              />
              <span className="slider-value">{story.chaptersCount} 章</span>
            </div>
            <div className="form-group">
              <label>叙事视角角色</label>
              <input
                type="text"
                value={story.povCharacter}
                onChange={(e) => handleStoryChange('povCharacter', e.target.value)}
                placeholder="主要叙述角色是谁？"
              />
            </div>
          </div>

          <div className="input-section">
            <h3>角色创建</h3>
            <div className="form-group">
              <label>角色姓名</label>
              <input
                type="text"
                value={characterInput.name}
                onChange={(e) => handleCharacterChange('name', e.target.value)}
                placeholder="输入角色姓名"
              />
            </div>
            <div className="form-group">
              <label>角色职能</label>
              <select
                value={characterInput.role}
                onChange={(e) => handleCharacterChange('role', e.target.value)}
              >
                <option value="主角">主角</option>
                <option value="反派">反派</option>
                <option value="配角">配角</option>
                <option value="次要">次要</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div className="form-group">
              <label>角色描述</label>
              <textarea
                value={characterInput.description}
                onChange={(e) => handleCharacterChange('description', e.target.value)}
                placeholder="描述角色的特征、性格等..."
                rows={3}
              ></textarea>
            </div>
            <button onClick={addCharacter} className="secondary-btn">添加角色</button>
          </div>

          {characters.length > 0 && (
            <div className="input-section characters-list">
              <h3>已创建角色</h3>
              {characters.map((char, index) => (
                <div key={char.id} className="character-item">
                  <h4>{char.name} ({char.role})</h4>
                  <p>{char.description}</p>
                </div>
              ))}
            </div>
          )}
        </aside>

        <main className="workspace-main">
          <div className="writing-area">
            <h3>章节写作</h3>
            <div className="chapter-display">
              <textarea
                value={currentChapter}
                onChange={(e) => setCurrentChapter(e.target.value)}
                placeholder="章节内容将显示在这里..."
                rows={15}
                disabled={agentStatus.isRunning}
              ></textarea>
            </div>

            <div className="progress-section">
              <h4>写作进度</h4>
              <div className="progress-bar-container">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${storyProgress}%` }}
                ></div>
              </div>
              <span className="progress-text">{Math.round(storyProgress)}% 完成</span>
            </div>

            <div className="agent-control-section">
              <h4>AI代理控制</h4>
              <div className="agent-status">
                <div className={`status-indicator ${agentStatus.isRunning ? 'running' : 'idle'}`}></div>
                <span className="status-text">{agentStatus.message} | 活跃代理: {agentStatus.activeAgents}</span>
              </div>
              <div className="agent-buttons">
                <button
                  onClick={handleStartWriting}
                  className="primary-btn"
                  disabled={agentStatus.isRunning}
                >
                  开始写作
                </button>
                <button className="secondary-btn">暂停</button>
                <button className="danger-btn">停止</button>
              </div>
            </div>
          </div>

          <div className="feedback-section">
            <h3>人类反馈</h3>
            <div className="feedback-input">
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="对当前章节提供反馈或建议修改..."
                rows={4}
              ></textarea>
            </div>
            <div className="feedback-actions">
              <button className="primary-btn">批准章节</button>
              <button onClick={handleFeedback} className="secondary-btn">请求修订</button>
              <button className="secondary-btn">建议修改</button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default StoryWorkspace;