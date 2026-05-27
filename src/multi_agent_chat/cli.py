"""
CLI interface for multi-agent-chat using Rich for beautiful terminal output.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .loader import load_all_agents, load_agent
from .engine import ConversationEngine
from .models import Conversation
from .storage import ConversationStorage


console = Console()


def print_message(agent_name: str, content: str, role: str = "assistant") -> None:
    """
    Print a formatted message from an agent.
    
    Args:
        agent_name: Name of the agent
        content: Message content
        role: Role of the sender (system, assistant, user)
    """
    # Choose color based on agent name (consistent coloring)
    colors = ["blue", "green", "yellow", "magenta", "cyan", "red"]
    color_idx = hash(agent_name) % len(colors)
    color = colors[color_idx]
    
    if role == "system":
        # System messages in dim gray
        console.print(Panel(
            Text(content, style="dim"),
            title="[dim]System[/dim]",
            border_style="dim",
            box=box.ROUNDED
        ))
    else:
        # Agent messages with their color
        console.print(Panel(
            Text(content),
            title=f"[bold {color}]{agent_name}[/bold {color}]",
            border_style=color,
            box=box.ROUNDED
        ))


def print_welcome(agents: list, topic: Optional[str] = None) -> None:
    """Print welcome message and conversation info."""
    # Create agents table
    table = Table(
        title="Participating Agents",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Name", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Model", style="yellow")
    
    for agent in agents:
        table.add_row(agent.name, agent.role, agent.model)
    
    console.print()
    console.print(Panel(
        "[bold]Multi-Agent Chat CLI[/bold]\n\n"
        "A round-based conversation system for AI agents.",
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
) -> None:
    """
    Run a multi-agent conversation.
    
    Args:
        agents_dir: Directory containing agent JSON files
        topic: Optional conversation topic
        rounds: Number of conversation rounds
        output: Optional path to save conversation JSON
    """
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
    
    # Print welcome
    print_welcome(agents, topic)
    
    # Create conversation
    conversation_id = f"conv_{asyncio.get_event_loop().time():.0f}"
    conversation = Conversation(id=conversation_id, topic=topic)
    
    # Run conversation
    async with ConversationEngine(conversation, agents) as engine:
        console.print("[dim]Starting conversation...[/dim]\n")
        
        # Add topic as system message if provided
        if topic:
            print_message("System", f"The topic of this conversation is: {topic}", role="system")
        
        for round_num in range(rounds):
            console.print(f"[dim]--- Round {round_num + 1}/{rounds} ---[/dim]\n")
            
            for agent in agents:
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
        description="Multi-Agent Chat CLI - Round-based conversations between AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --agents ./examples/agents
  %(prog)s --agents ./examples/agents --topic "Climate Change" --rounds 5
  %(prog)s --agents ./examples/agents --output conversation.json
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
        "--version", "-v",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Run the async conversation
    try:
        asyncio.run(run_conversation(
            agents_dir=args.agents,
            topic=args.topic,
            rounds=args.rounds,
            output=args.output,
        ))
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Conversation interrupted by user.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
