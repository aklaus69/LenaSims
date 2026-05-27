"""
Human agent implementation - allows real user participation in conversations.
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

from .models import AgentConfig, Message

console = Console()


class HumanAgent:
    """
    A human participant in the conversation.
    Waits for user input instead of calling an LLM.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.is_human = True
    
    async def get_response(self, conversation_history: list, topic: Optional[str] = None) -> str:
        """
        Get response from human user.
        
        Args:
            conversation_history: List of previous messages
            topic: Current conversation topic
            
        Returns:
            Human's input
        """
        # Show context
        console.print()
        
        # Header
        header_text = f"🧑‍💻 MENSCHLICHER TEILNEHMER: {self.name}"
        if topic:
            header_text += f"\nThema: {topic}"
        
        console.print(Panel(
            header_text,
            border_style="bright_yellow",
            box=box.DOUBLE
        ))
        
        # Show last few messages for context
        if conversation_history:
            console.print("[dim]Letzte Nachrichten:[/dim]")
            for msg in conversation_history[-3:]:  # Last 3 messages
                agent_emoji = self._get_agent_emoji(msg.agent_id or "Unknown")
                content_short = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
                console.print(f"  {agent_emoji} [cyan]{msg.agent_id or 'Unknown'}:[/cyan] {content_short}")
            console.print()
        
        # Get input
        console.print("[bold yellow]📝 Deine Nachricht[/bold yellow] (ENTER zum Überspringen, 'exit' zum Beenden):")
        
        try:
            user_input = console.input("[bold]> [/bold]").strip()
        except (EOFError, KeyboardInterrupt):
            return "[übersprungen]"
        
        if user_input.lower() == 'exit':
            raise KeyboardInterrupt("User requested exit")
        
        if user_input == "":
            return "[schweigt und hört zu]"
        
        return user_input
    
    def _get_agent_emoji(self, agent_name: str) -> str:
        """Get emoji for agent name."""
        emojis = {
            "Klaus": "🔧",
            "Maria": "🎨",
            "Isabella": "☕",
            "Oskar": "😒",
            "Sophie": "🌈",
            "Professor": "📚",
        }
        return emojis.get(agent_name, "🤖")
    
    def __repr__(self) -> str:
        return f"HumanAgent(name='{self.name}')"


def create_human_agent(
    name: str = "Klaus (Du)",
    role: str = "Menschlicher Teilnehmer",
    instructions: str = "Du bist ein realer Mensch, der mit den KI-Agenten interagiert.",
) -> AgentConfig:
    """
    Create a human agent configuration.
    
    Args:
        name: Display name for the human
        role: Role description
        instructions: Instructions (mostly for documentation)
        
    Returns:
        AgentConfig for human participant
    """
    return AgentConfig(
        name=name,
        role=role,
        instructions=instructions,
        model="human",  # Special marker
        temperature=0.0,  # Not used for humans
    )


def should_use_human_agents(agents: list) -> bool:
    """
    Check if any agent is a human (marked with model='human').
    
    Args:
        agents: List of AgentConfig objects
        
    Returns:
        True if at least one human agent exists
    """
    return any(agent.model == "human" for agent in agents)


def add_human_agent_option() -> Optional[AgentConfig]:
    """
    Interactive prompt to add a human agent.
    
    Returns:
        AgentConfig for human, or None if declined
    """
    console.print()
    console.print(Panel(
        "[bold]🧑‍💻 MENSCHLICHER TEILNEHMER[/bold]\n\n"
        "Möchtest du selbst am Gespräch teilnehmen?",
        border_style="yellow",
        box=box.DOUBLE
    ))
    
    console.print("[dim]Du kannst nach jeder Runde antworten und die KI-Agenten beeinflussen.[/dim]")
    console.print()
    
    choice = console.input("[bold]Menschlichen Agenten hinzufügen?[/bold] [j/n, ENTER=j]: ").strip().lower()
    
    if choice not in ("", "j", "ja", "y", "yes"):
        return None
    
    # Ask for name
    name = console.input("[bold]Dein Name[/bold] [ENTER='Klaus (Du)']: ").strip()
    if name == "":
        name = "Klaus (Du)"
    
    # Ask for role
    role = console.input("[bold]Deine Rolle[/bold] [ENTER='Menschlicher Teilnehmer']: ").strip()
    if role == "":
        role = "Menschlicher Teilnehmer"
    
    console.print(f"[green]✅ Menschlicher Agent '{name}' hinzugefügt![/green]")
    
    return create_human_agent(name=name, role=role)


async def run_conversation_with_humans(
    engine,
    agents: list,
    rounds: int,
    human_agents: list,
) -> None:
    """
    Run conversation with human participation.
    
    Args:
        engine: ConversationEngine instance
        agents: List of all agents (AI + human)
        rounds: Number of rounds
        human_agents: List of HumanAgent instances
    """
    from .cli import print_message
    
    human_agents_by_name = {ha.config.name: ha for ha in human_agents}
    
    for round_num in range(rounds):
        console.print(f"[dim]--- Round {round_num + 1}/{rounds} ---[/dim]\n")
        
        for agent in agents:
            # Check if this is a human agent
            if agent.name in human_agents_by_name:
                human = human_agents_by_name[agent.name]
                
                # Get conversation history
                history = engine.conversation.messages
                
                # Get human input
                try:
                    response = await human.get_response(
                        history,
                        topic=engine.conversation.topic
                    )
                except KeyboardInterrupt:
                    console.print("\n[yellow]Gespräch vom Benutzer beendet.[/yellow]")
                    return
                
                # Add to conversation
                message = Message(
                    role="assistant",
                    content=response,
                    agent_id=agent.name
                )
                engine.conversation.messages.append(message)
                print_message(agent.name, response)
                
            else:
                # AI agent
                try:
                    message = await engine.run_round(current_agent=agent)
                    print_message(message.agent_id or "Unknown", message.content)
                except Exception as e:
                    console.print(f"[red]Error from {agent.name}:[/red] {e}")