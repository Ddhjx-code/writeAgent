# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# AI Collaborative Novel Writing System

A powerful system that combines human creativity with AI assistance to enable collaborative novel writing between humans and AI agents. The system uses multiple specialized agents, a knowledge base for story continuity, and an intuitive interface to facilitate the writing process.

## Project Structure

The AI Cooperative Novel Writing System is divided into several key modules:

- **Agents**: Specialized AI agents for different aspects of the writing process (`src/agents/`)
- **Workflow**: LangGraph-based workflow orchestration for multi-agent collaboration (`src/workflow/`)
- **LLM**: LLM provider utilities and management (`src/llm/`)
- **Knowledge Base**: Persistent storage and retrieval layer for story information (`src/knowledge/`)
- **Communication**: Communication between agents
- **Interface**: React web interface for user interaction (`src/frontend/`)
- **API**: FastAPI backend server with RESTful endpoints (`src/api/`)
- **Core**: Main engine and system integration components (`src/core/`)

## Architecture Overview

The system uses a multi-agent approach with 9 specialized AI agents that work together through a hierarchical LangGraph workflow:

- **PlannerAgent**: Develops story structures and outlines
- **WriterAgent**: Creates narrative content
- **ArchivistAgent**: Maintains story continuity and metadata
- **EditorAgent**: Reviews content for quality and coherence
- **ConsistencyCheckerAgent**: Ensures narrative consistency
- **DialogueSpecialistAgent**: Enhances character dialogue
- **WorldBuilderAgent**: Develops fictional worlds and settings
- **PacingAdvisorAgent**: Optimizes story rhythm and pacing
- **HumanizerAgent**: Removes AI writing artifacts for more natural text

The agents collaborate through a hierarchical LangGraph state machine (`src/workflow/graph.py`) that manages the workflow between three different phases of the writing process (macro, mid, micro) using `src/workflow/phase_manager.py`.

### Hierarchical Phase Management
- **Macro**: High-level story architecture, world building, and character frameworks
- **Mid**: Chapter organization and character integration planning
- **Micro**: Detailed chapter writing and refinement

## Key Components

### Writing Engine
Located in `src/core/engine.py`, this orchestrates the entire system including:
- Agent initialization and management
- Knowledge store integration
- Story state management
- API endpoint handling

### LLM Providers
Located in `src/llm/providers.py`, this manages unified interface for multiple LLM providers including:
- OpenAI models (GPT-4, GPT-3.x series)
- Anthropic models (Claude 2.x, 3.x)
- Mistral models
- Cohere models
- Base URL configurations for API endpoints

### Knowledge Store
Uses both ChromaDB and LlamaIndex backends for:
- Storing story elements, characters, and world details
- Maintaining story continuity across generation cycles
- Providing context to agents

### Workflow System
Based on LangGraph with specialized nodes for each agent (`src/workflow/nodes.py`) and hierarchical phase management (`src/workflow/phase_manager.py`):
- Defines conditional edges between different writing phases
- Manages state using GraphState
- Tracks chapter progress and story metrics across hierarchical levels
- Enables transitions between macro (story-level), mid (chapter-level), and micro (content-level) phases

## Development Commands

### Running the System
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize configuration via environment variables:
export OPENAI_API_KEY='your-key-here'
export ANTHROPIC_API_KEY='your-key-here'  # if using Claude

# Launch the interactive CLI
python -m src.main

# Create and run a simple story
python -m src.main --create-story --run-story

# Launch the web interface (NEW):
# 1. Start the API backend:
uvicorn src.api.server:app --host 0.0.0.0 --port 8000

# 2. In another terminal, start the React frontend:
cd src/frontend && npm install && npm run dev
```

### Testing
The project includes several tests in the `tests/` directory:
- `test_agents.py`: Agent functionality tests
- `test_workflow.py`: Workflow tests
- `test_knowledge.py`: Knowledge base tests

Run all tests:
```bash
python -m pytest tests/
```

Run individual test files:
```bash
python -m pytest tests/test_agents.py
```

## Configuration

The system is configured through environment variables:
- `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`/`MISTRAL_API_KEY`/`COHERE_API_KEY`: API keys for different LLM providers
- `WRITER_MODEL`/`EDITOR_MODEL`/`PLANNER_MODEL`: Specify which models to use for different agents
- `CHROMA_PERSIST_DIR`: Storage directory for Chroma database (default: ./chroma_data)
- `LLAMAINDEX_STORAGE_DIR`: Storage directory for LlamaIndex (default: ./llamaindex_storage)
- `MAX_ITERATIONS`: Maximum iterations for story generation (default: 10)
- `MAX_RETRY_ATTEMPTS`: Maximum retry attempts for failed operations (default: 3)

## Key Files and Classes

- `src/main.py`: Main entry point and CLI interface
- `src/config.py`: Configuration management
- `src/core/engine.py`: Main writing engine
- `src/workflow/graph.py`: LangGraph workflow orchestration
- `src/workflow/nodes.py`: Node definitions for each agent
- `src/workflow/state.py`: Graph state definition
- `src/api/server.py`: FastAPI backend server
- `src/api/types.py`: API type definitions
- `src/frontend/src/`: React components and UI
- `src/frontend/package.json`: Frontend dependencies