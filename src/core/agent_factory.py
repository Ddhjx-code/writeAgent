from typing import Dict, Any, Optional
from src.agents.base import BaseAgent, AgentConfig
try:
    from src.core.knowledge_base import KnowledgeBase  # Original full knowledge base
except ImportError:
    from src.core.knowledge_base_minimal import KnowledgeBase  # Fallback minimal version
import importlib


class AgentFactory:
    """
    Factory class to create and manage different types of agents
    in the novel writing system.
    """

    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
        self.agents: Dict[str, BaseAgent] = {}

        # Default LLM configuration using a local/mocked model to avoid API dependencies
        # This fallback allows the system to work without requiring OpenAI or other proprietary API keys
        self.default_llm_config = {
            "model": "local",  # Use local/model-agnostic configuration
            "use_local": True,
            "fallback": True
        }

    def create_agent(self, agent_type: str, name: str, **kwargs) -> BaseAgent:
        """
        Create an instance of a specific agent type
        """
        # Define all possible agent types and their module paths
        agent_modules = {
            "writer": "src.agents.writer",
            "planner": "src.agents.planner",
            "archivist": "src.agents.archivist",
            "editor": "src.agents.editor",
            "consistency_checker": "src.agents.consistency_checker",
            "dialogue_specialist": "src.agents.dialogue_specialist",
            "world_builder": "src.agents.world_builder",
            "pacing_advisor": "src.agents.pacing_advisor"
        }

        if agent_type not in agent_modules:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Get the module path
        module_path = agent_modules[agent_type]

        # Prepare agent configuration
        config = AgentConfig(
            name=name,
            role=kwargs.get("role", f"{agent_type.replace('_', ' ').title()} Agent"),
            llm_config=kwargs.get("llm_config", self.default_llm_config),
            system_message=kwargs.get("system_message", f"You are a {agent_type.replace('_', ' ')} agent helping with novel writing."),
            max_consecutive_auto_reply=kwargs.get("max_consecutive_auto_reply", 10),
            human_input_mode=kwargs.get("human_input_mode", "NEVER")
        )

        # Import the agent class dynamically
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, f"{agent_type.replace('_', ' ').title().replace(' ', '')}Agent")
            agent_instance = agent_class(config=config, knowledge_base=self.knowledge_base, **kwargs)
            self.agents[name] = agent_instance
            return agent_instance
        except ImportError as e:
            # If the agent module doesn't exist yet, create a generic agent
            print(f"Agent module {module_path} not found, creating base agent: {e}")
            from src.agents.base import BaseAgent
            agent_instance = BaseAgent(config=config, knowledge_base=self.knowledge_base)
            self.agents[name] = agent_instance
            return agent_instance

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)

    def list_agents(self) -> Dict[str, str]:
        """Get a list of all created agents and their types"""
        return {name: agent.__class__.__name__ for name, agent in self.agents.items()}

    def create_all_agents(self):
        """Create all the agents for the novel writing system"""
        agents_to_create = [
            {
                "type": "archivist",
                "name": "Archivist",
                "role": "Document Management Agent responsible for managing characters, world settings, and document versions",
                "system_message": "You are an Archivist Agent responsible for managing the novel's documentation. This includes maintaining character cards, world settings, chapter versions, and ensuring consistency in the story's documentation."
            },
            {
                "type": "planner",
                "name": "Planner",
                "role": "Story Planner Agent responsible for designing story main thread, chapter outlines, and plot points",
                "system_message": "You are a Planner Agent responsible for designing the story's main thread, chapter outlines, and plot points. Your job is to create a coherent and engaging narrative structure."
            },
            {
                "type": "writer",
                "name": "Writer",
                "role": "Main Writer Agent responsible for generating chapter content",
                "system_message": "You are a Writer Agent responsible for generating the main content of chapters. Your task is to create compelling, well-written prose that follows the story outline and maintains the established style and tone."
            },
            {
                "type": "editor",
                "name": "Editor",
                "role": "Editor Agent focused on readability, emotional tension, and avoiding redundancy",
                "system_message": "You are an Editor Agent focused on improving readability, emotional tension, and eliminating redundancy in the story content."
            },
            {
                "type": "consistency_checker",
                "name": "ConsistencyChecker",
                "role": "Consistency Checker Agent focused on timeline, character behavior, and causal chains",
                "system_message": "You are a Consistency Checker Agent focused on ensuring timeline consistency, character behavior coherence, and proper causal chains throughout the novel."
            },
            {
                "type": "world_builder",
                "name": "WorldBuilder",
                "role": "World Builder Agent responsible for rich scene details and sensory descriptions",
                "system_message": "You are a World Builder Agent responsible for creating rich scene details and vivid sensory descriptions that enhance the setting and atmosphere of the story."
            },
            {
                "type": "dialogue_specialist",
                "name": "DialogueSpecialist",
                "role": "Dialogue Specialist Agent focused on character dialogue style, tone, and subtext",
                "system_message": "You are a Dialogue Specialist Agent focused on optimizing character dialogue to match their personality and speech patterns, with attention to subtext and underlying emotions."
            },
            {
                "type": "pacing_advisor",
                "name": "PacingAdvisor",
                "role": "Pacing Advisor Agent controlling story pace, suspense density, and paragraph distribution",
                "system_message": "You are a Pacing Advisor Agent responsible for controlling the rhythm and pacing of the narrative, managing suspense density, and improving paragraph structure and flow."
            }
        ]

        created_agents = {}
        for agent_config in agents_to_create:
            agent = self.create_agent(agent_config["type"], agent_config["name"],
                                    role=agent_config["role"],
                                    system_message=agent_config["system_message"])
            created_agents[agent.name] = agent

        return created_agents