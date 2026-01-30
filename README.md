# AI Collaborative Novel Writing System

A sophisticated multi-agent system for collaborative novel writing that combines AI agents with human creative input. The system implements 8 specialized AI agents coordinated through a LangGraph workflow to create professionally structured and coherent novels.

## System Architecture

The system follows a LangGraph + AutoGen + LlamaIndex architecture with 8 specialized agents:

1. **Archivist Agent** - Document management agent responsible for managing characters, world settings, and document versions
2. **Planner Agent** - Story planning agent responsible for designing story main thread, chapter outlines, and plot points
3. **Writer Agent** - Main content generation agent responsible for generating chapter content
4. **Editor Agent** - Focused on readability, emotional tension, and avoiding redundancy
5. **Consistency Checker Agent** - Ensures timeline consistency, character behavior coherence, and proper causal chains
6. **Dialogue Specialist Agent** - Optimizes character dialogue to match their personality and speech patterns
7. **World Builder Agent** - Creates rich scene details and sensory descriptions
8. **Pacing Advisor Agent** - Controls narrative rhythm and manages suspense density

## Project Structure

```
writeAgent/
├── src/
│   ├── agents/           # Specialized AI agents implementation
│   │   ├── base.py       # Base agent class
│   │   ├── archivist.py  # Archivist agent
│   │   ├── writer.py     # Writer agent
│   │   ├── planner.py    # Planner agent
│   │   ├── editor.py     # Editor agent
│   │   ├── consistency_checker.py  # Consistency checker
│   │   ├── dialogue_specialist.py  # Dialogue specialist
│   │   ├── world_builder.py        # World builder
│   │   └── pacing_advisor.py       # Pacing advisor
│   ├── core/             # Core functionality modules
│   │   ├── knowledge_base.py      # Knowledge base implementation
│   │   ├── story_state.py         # Story state management
│   │   ├── agent_factory.py       # Agent factory
│   │   └── workflow.py            # LangGraph workflow
│   └── ui/               # User interface
│       └── gradio_app.py        # Gradio frontend application
├── tests/                # Test cases
├── docs/                 # Documentation
├── prompts/              # Agent prompts
├── config/               # Configuration files
├── examples/             # Example code
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Project configuration
```

## Features

- **Centralized Knowledge Base**: Using LlamaIndex + Chroma for character, location, and plot point management
- **Advanced State Management**: Complete story state tracking with chapter status, character development, etc.
- **Coordinated Workflow**: LangGraph-managed orchestration of AI agents
- **Human-in-the-Loop**: Integration points for human creative input and feedback
- **Multi-Agent Architecture**: 8 specialized agents each focused on specific aspects of novel creation
- **Rich UI Interface**: Gradio-based web interface for human interaction
- **Version Control**: Git-based system for tracking creative changes

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application with:
```bash
python src/ui/gradio_app.py
```

The application will start a web interface at `http://localhost:7860` where you can:

1. Create a new story with title, genre, and summary
2. Define characters and their characteristics
3. Set up locations and world details
4. Generate chapters using the AI workflow
5. Monitor the multi-agent collaboration process
6. Query the knowledge base
7. Review and edit content

## Agent Workflows

The system implements multiple workflows that coordinate the specialized agents:

1. **Chapter Writing Workflow**: Planning → Writing → Review → Editing → Archiving
2. **Consistency Checking Workflow**: Timeline → Character → Causal → World Building
3. **Dialogue Enhancement Workflow**: Character Voice → Subtext → Realism → Flow
4. **Quality Assurance Workflow**: Style → Readability → Pacing → Final Review

## Technology Stack

- **Multi-Agent Framework**: AutoGen + LangGraph
- **Knowledge Base**: LlamaIndex + ChromaDB
- **LLM Integration**: OpenAI-compatible API interface with support for Claude and GPT models
- **Frontend Interface**: Gradio
- **State Management**: Pydantic models

## Configuration

The system can be configured in `config/` for different API endpoints, model settings, and workflow patterns. Special support is included for the API endpoint at `https://apis.iflow.cn/v1/` with Claude and GPT model integration.

## Contributing

The project follows the implementation plan detailed in `plan.md` for system architecture and agent design. Contributions are welcome, especially:

- Additional agent types for specialized use cases
- Enhanced UI/UX interfaces
- Additional language support
- Improved content generation algorithms
- Advanced consistency checking logic