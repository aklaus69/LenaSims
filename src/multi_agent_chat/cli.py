"""
CLI interface for multi-agent-chat using Rich for beautiful terminal output.
Supports both AI agents and human participants.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .loader import load_all_agents, load_agent
from .engine import ConversationEngine
from .models import Conversation, Message
from .storage import ConversationStorage
from .model_selector import interactive_model_selection
from .agent_configurator import interactive_agent_configuration
from .human_agent import (
    HumanAgent, 
    create_human_agent, 
    add_human_agent_option,
    should_use_human_agents
)


console = Console()


def print_message(agent_name: str, content: str, role: str = "assistant") -> None:
    """Print a formatted message from an agent."""
    colors = ["blue", "green", "yellow", "magenta", "cyan", "red"]
    color_idx = hash(agent_name) % len(colors)
    color = colors[color_idx]
    
    # Special styling for human
    is_human = "(Du)" in agent_name or agent_name.endswith(" (Human)")
    
    if role == "system":
        console.print(Panel(
            Text(content, style="dim"),
            title="[dim]System[/dim]",
            border_style="dim",
            box=box.ROUNDED
        ))
    elif is_human:
        # Human messages with special styling
        console.print(Panel(
            Text(content, style="bold yellow"),
            title=f"[bold bright_yellow]🧑‍💻 {agent_name}[/bold bright_yellow]",
            border_style="bright_yellow",
            box=box.DOUBLE
        ))
    else:
        # AI agent messages
        console.print(Panel(
            Text(content),
            title=f"[bold {color}]{agent_name}[/bold {color}]",
            border_style=color,
            box=box.ROUNDED
        ))


def print_welcome(agents: list, topic: Optional[str] = None) -> None:
    """Print welcome message and conversation info."""
    table = Table(
        title="Participating Agents",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Name", style="cyan")
    table.add_column("Rolle/Type", style="green")
    table.add_column("Modell", style="yellow")
    table.add_column("Temp", style="magenta")
    
    for agent in agents:
        role_short = agent.role[:30] + "..." if len(agent.role) > 30 else agent.role
        model_short = "🧑‍💻 MENSCH" if agent.model == "human" else (agent.model.split(":")[0] if ":" in agent.model else agent.model)
        temp_str = "—" if agent.model == "human" else f"{agent.temperature:.1f}"
        
        table.add_row(agent.name, role_short, model_short, temp_str)
    
    console.print()
    console.print(Panel(
        "[bold]Multi-Agent Chat CLI[/bold]\n\n"
        "Round-based conversations between AI agents and humans.",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    if topic:
        console.print(Panel(
            f"[bold]Topic:[/bold] {topic}",
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
    
    console.print(table)
    console.print()
    
    # Show controls if human is present
    if any(agent.model == "human" for agent in agents):
        console.print(Panel(
            "[bold yellow]🧑‍💻 HUMAN MODE ACTIVE[/bold yellow]\n"
            "Du kannst in jeder Runde antworten.\n"
            "Tippe deine Nachricht und drücke ENTER.\n"
            "LEER = überspringen | 'exit' = beenden",
            border_style="bright_yellow",
            box=box.ROUNDED
        ))
        console.print()


def print_summary(conversation: Conversation) -> None:
    """Print conversation summary."""
    console.print()
    console.print(Panel(
        f"[bold green]Conversation Complete![/bold green]\n\n"
        f"Total Messages: {len(conversation.messages)}\n"
        f"Participants: {', '.join(conversation.participants)}\n"
        f"Started: {conversation.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        border_style="green",
        box=box.DOUBLE
    ))


async def run_conversation(
    agents_dir: Path,
    topic: Optional[str],
    rounds: int,
    output: Optional[Path],
    interactive_model: bool = False,
    configure: bool = False,
    include_human: bool = False,
) -> None:
    """
    Run a multi-agent conversation with optional human participation.
    """
    from .loader import load_all_agents
    
    # Load agents
    try:
        agents = load_all_agents(agents_dir)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Agents directory not found: {agents_dir}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error loading agents:[/red] {e}")
        sys.exit(1)
    
    if not agents:
        console.print(f"[red]Error:[/red] No agents found in {agents_dir}")
        sys.exit(1)
    
    # Full configuration
    if configure:
        interactive_agent_configuration(agents)
    elif interactive_model:
        interactive_model_selection(agents)
    
    # Add human agent if requested
    human_config = None
    if include_human:
        human_config = add_human_agent_option()
        if human_config:
            agents.append(human_config)
    
    # Print welcome
    print_welcome(agents, topic)
    
    # Create conversation
    conversation_id = f"conv_{asyncio.get_event_loop().time():.0f}"
    conversation = Conversation(id=conversation_id, topic=topic)
    
    # Prepare human agent handling
    human_agents = {}
    if human_config:
        human_agents[human_config.name] = HumanAgent(human_config)
    
    # Run conversation
    async with ConversationEngine(conversation, agents) as engine:
        console.print("[dim]Starting conversation...[/dim]\n")
        
        # Add topic as system message
        if topic:
            print_message("System", f"The topic of this conversation is: {topic}", role="system")
        
        for round_num in range(rounds):
            console.print(f"[dim]--- Round {round_num + 1}/{rounds} ---[/dim]\n")
            
            for agent in agents:
                # Check if this is the human
                if agent.name in human_agents:
                    human = human_agents[agent.name]
                    
                    # Get conversation history for context
                    history = [m for m in conversation.messages if m.role != "system"][-5:]
                    
                    try:
                        response = await human.get_response(history, topic)
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Gespräch vom Benutzer beendet.[/yellow]")
                        return
                    
                    # Create message
                    message = Message(
                        role="assistant",
                        content=response,
                        agent_id=agent.name
                    )
                    conversation.messages.append(message)
                    if agent.name not in conversation.participants:
                        conversation.participants.append(agent.name)
                    print_message(agent.name, response)
                    
                else:
                    # AI agent
                    try:
                        message = await engine.run_round(current_agent=agent)
                        print_message(message.agent_id or "Unknown", message.content)
                    except Exception as e:
                        console.print(f"[red]Error from {agent.name}:[/red] {e}")
    
    # Print summary
    print_summary(conversation)
    
    # Save if output specified
    if output:
        try:
            storage = ConversationStorage(output.parent)
            storage.save(conversation, output.name)
            console.print(f"\n[green]Conversation saved to:[/green] {output}")
        except Exception as e:
            console.print(f"\n[red]Error saving conversation:[/red] {e}")


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="multi-agent-chat",
        description="Multi-Agent Chat CLI - Round-based conversations between AI agents and humans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --agents ./examples/agents
  %(prog)s --agents ./examples/agents --topic "Climate Change" --rounds 5
  %(prog)s --agents ./examples/agents --output conversation.json
  %(prog)s --agents ./examples/agents -i     # Interactive model selection
  %(prog)s --agents ./examples/agents -c     # Full agent configuration
  %(prog)s --agents ./examples/agents --human  # Include human participant
  %(prog)s --agents ./examples/agents -c --human  # Configure + human
        """
    )
    
    parser.add_argument(
        "--agents", "-a",
        type=Path,
        default=Path("./examples/agents"),
        help="Directory containing agent JSON files (default: ./examples/agents)"
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        default=None,
        help="Conversation topic"
    )
    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=3,
        help="Number of conversation rounds (default: 3)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file path to save conversation JSON"
    )
    parser.add_argument(
        "--interactive-model", "-i",
        action="store_true",
        help="Interactive model selection for each agent"
    )
    parser.add_argument(
        "--configure", "-c",
        action="store_true",
        help="Full agent configuration (names, personality, temperature)"
    )
    parser.add_argument(
        "--human", "-H",
        action="store_true",
        help="Include human participant in conversation"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 0.2.0"
    )
    
    args = parser.parse_args()
    
    # Run the async conversation
    try:
        asyncio.run(run_conversation(
            agents_dir=args.agents,
            topic=args.topic,
            rounds=args.rounds,
            output=args.output,
            interactive_model=args.interactive_model,
            configure=args.configure,
            include_human=args.human,
        ))
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Conversation interrupted by user.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
