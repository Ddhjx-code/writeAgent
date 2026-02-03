# AI Collaborative Novel Writing System

A powerful system that combines human creativity with AI assistance to enable collaborative novel writing between humans and AI agents. The system uses multiple specialized agents, a knowledge base for story continuity, and an intuitive interface to facilitate the writing process.

## Features

- **Multi-Agent Collaboration**: Uses 9 specialized AI agents:
  - WriterAgent: Creates narrative content
  - PlannerAgent: Develops story structures and outlines
  - ArchivistAgent: Maintains story continuity and metadata
  - EditorAgent: Reviews content for quality and coherence
  - ConsistencyCheckerAgent: Ensures narrative consistency
  - DialogueSpecialistAgent: Enhances character dialogue
  - WorldBuilderAgent: Develops fictional worlds and settings
  - PacingAdvisorAgent: Optimizes story rhythm and pacing
  - HumanizerAgent: Removes AI writing artifacts for more natural text

- **Knowledge Management**: Built-in knowledge base using both LlamaIndex and ChromaDB backends to track story elements, characters, and world details

- **Interactive Workflow**: Using LangGraph for complex multi-agent workflow orchestration

- **Human Feedback Integration**: Allows writers to review, approve, and provide feedback on generated content

- **Flexible Interface**: Gradio-based UI for easy interaction and story development

## System Architecture

The AI Cooperative Novel Writing System is divided into several key modules:

- **Agents**: Specialized AI agents for different aspects of the writing process
- **Workflow**: LangGraph-based workflow orchestration for multi-agent collaboration
- **Knowledge Base**: Persistent storage and retrieval layer for story information
- **Communication**: AutoGen-based communication between agents
- **Interface**: Gradio web interface for user interaction
- **Core**: Main engine and system integration components

## Prerequisites

- Python 3.8+
- Required packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd writeAgent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys in environment variables (or use a `.env` file):
   ```bash
   export OPENAI_API_KEY='your-key-here'
   export ANTHROPIC_API_KEY='your-key-here'  # if using Claude
   ```

## Usage

### Command-Line Interface

Run the system from the command line:

```bash
# Launch the interactive CLI
python -m src.main

# Create and run a simple story
python -m src.main --create-story --run-story

# Launch the web interface
python -m src.main --ui

# Share the web interface
python -m src.main --ui --interface-share
```

### Web Interface

1. Start the web application:
   ```bash
   python -m src.main --ui
   ```

2. Open your browser to the displayed URL (typically http://localhost:7860)

3. Use the interface to:
   - Define your story concept and characters
   - Generate chapters using AI agents
   - Review and provide feedback
   - Visualize story elements
   - Export your final work

## Configuration

The system uses a flexible configuration system:

- `src/config.py`: Core configuration options
- Environment variables: API keys and model selection

The default configuration can be customized using environment variables:

```bash
export WRITER_MODEL="gpt-3.5-turbo"  # Specify writer model
export CHROMA_PERSIST_DIR="./my_chroma"  # Custom storage for Chroma
export LLAMAINDEX_STORAGE_DIR="./my_llamaindex"  # Custom storage for LlamaIndex
```

## Project Structure

```
writeAgent/
├── src/
│   ├── agents/           # AI agent implementations
│   ├── knowledge/        # Knowledge base management
│   ├── workflow/         # LangGraph workflow definitions
│   ├── communication/    # Agent communication layer
│   ├── interface/        # Web interface components
│   ├── core/             # Core system components
│   ├── config.py         # System configuration
│   ├── types.py          # Shared type definitions
│   └── exceptions.py     # System exceptions
├── tests/
│   ├── test_agents.py    # Agent functionality tests
│   ├── test_workflow.py  # Workflow tests
│   └── test_knowledge.py # Knowledge base tests
├── prompts/              # Agent prompt templates
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python -m pytest tests/test_agents.py
```

## Development

To contribute to the project:

1. Fork the repository
2. Set up your development environment
3. Create a feature branch
4. Submit a pull request with your changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions, please file an issue in the repository.

## Acknowledgments

- Built using LangGraph for workflow orchestration
- Powered by various LLMs for content generation
- Knowledge base management with ChromaDB and LlamaIndex