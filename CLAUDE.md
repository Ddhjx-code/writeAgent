# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

AI协作小说写作系统是一个复杂的多智能体系统，促进人类作家与8个专业AI智能体之间的协作小说创作。该系统采用LangGraph + AutoGen + LlamaIndex架构，通过结构化工作流协调专业智能体。

## 系统架构

系统遵循以下分层架构：

1. **核心层** (`src/core/`)
   - `story_state.py`: 管理故事的完整状态，包括角色、地点、章节及版本跟踪
   - `knowledge_base.py`: 使用LlamaIndex和ChromaDB的集中式知识仓库
   - `agent_factory.py`: 创建和管理所有专业AI智能体
   - `workflow.py`: 基于LangGraph的智能体间工作流协调

2. **智能体层** (`src/agents/`)
   - 8个专业智能体，分别处理小说写作的不同方面
   - 具有通用功能的基类智能体

3. **UI层** (`src/ui/`)
   - 用于人机协作的基于Gradio的网页界面

## 核心功能

1. **8个专业AI智能体**:
   - **文档管理员智能体**: 文档管理和版本控制
   - **规划员智能体**: 故事规划和章节大纲创建
   - **作家智能体**: 章节内容生成
   - **编辑智能体**: 可读性和张力优化
   - **一致性检查员**: 时间线、角色行为和因果链验证
   - **对话专家**: 角色对话优化
   - **世界构建者**: 场景细节和感官描述
   - **节奏顾问**: 叙述节奏和悬念管理

2. **综合状态管理**:
   - 完整的故事生命周期跟踪
   - 角色和地点管理
   - 章节内容及版本历史
   - 章节状态（草稿、评审、批准等）

3. **集中式知识库**:
   - 使用与ChromaDB集成的LlamaIndex作为向量存储
   - 支持语义搜索进行一致性检查
   - 面向本地模型的Ollama嵌入适配器
   - 实体关系跟踪

4. **多智能体工作流**:
   - 使用LangGraph进行有状态协调
   - 全局规划后跟章节处理
   - 人机协作检查点
   - 修订循环的条件循环

## 开发设置

1. **环境配置**:
   - 在config目录创建`.env`文件
   - 设置OpenAI/Anthropic API密钥
   - 示例`.env`结构:
   ```
   OPENAI_API_KEY=<your_api_key>
   ANTHROPIC_API_KEY=<your_anthropic_key>
   OPENAI_BASE_URL=<custom_endpoint_if_needed>
   OLLAMA_EMBEDDING_MODEL=qwen3-embedding:0.6b
   ```

2. **依赖安装**:
   - 运行 `pip install -r requirements.txt` 或 `pip install .`
   - Python版本要求: 3.9+ (推荐3.10+)

3. **依赖包**:
   - `pyautogen>=0.2.0` - 多智能体框架
   - `langgraph>=0.0.48` - 工作流编排
   - `llama-index>=0.10.0` & `chromadb>=0.4.0` - 知识库
   - `openai>=1.0.0` & `anthropic>=0.5.0` - LLM集成
   - `gradio>=4.0.0` - 前端界面
   - 其他: `pydantic`, `python-dotenv`, `sentence-transformers`

## 开发命令

1. **运行系统**:
   - 启动UI: `python src/ui/gradio_app.py`
   - UI将启动于 `http://localhost:7861`

2. **测试**:
   - 单元测试: `python -m pytest tests/`
   - 基本功能测试: `python -m pytest tests/test_basic_integration.py`
   - 集成测试: `python -m pytest tests/test_integration.py`
   - 系统验证: `python validate_system.py`

3. **演示**:
   - 运行演示: `python run_demo.py`

4. **系统验证**:
   - `python validate_system.py` - 验证整个系统实现

## 测试流程

1. **单元测试** (`tests/test_basic_integration.py`):
   - 测试基本智能体功能
   - 验证核心模型（StoryState，Character，Location，Chapter）
   - 验证UI组件功能

2. **集成测试** (`tests/test_integration.py`):
   - 完整工作流验证
   - 多智能体协作模式
   - 知识库与故事状态的集成
   - UI应用程序初始化

3. **系统验证** (`validate_system.py`):
   - 验证目录结构
   - 确认所有必需文件存在
   - 测试最少的导入和功能
   - 确认所有智能体都能创建

## 关键配置说明

1. **API密钥**:
   - API密钥存储在 `config/.env`
   - 支持OpenAI和Anthropic APIs
   - 降级实现在没有API密钥的情况下允许测试

2. **知识库配置**:
   - 使用ChromaDB进行存储，位于 `./storage/`
   - 钢向本地嵌入模型的Ollama嵌入适配器
   - 支持多种嵌入模型（`qwen3-embedding:0.6b`）

3. **工作流配置**:
   - 实现两阶段架构：
     - 第一阶段：全局规划（故事弧线创建）
     - 第二阶段：按章节处理，带有条件循环
   - 在LangGraph中的条件边用于循环控制