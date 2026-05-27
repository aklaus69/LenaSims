"""
Interactive model selection for agents.
Inspired by three_agents_chat.py - allows per-agent model selection.
"""

from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# Available Ollama models with descriptions
AVAILABLE_MODELS = {
    "1": ("kimi-k2.5:cloud", "Kimik2.5 Cloud - Großes Modell, tiefes Verständnis", "🧠"),
    "2": ("gemini-3-flash-preview:latest", "Gemini Flash - Schnell, kreativ", "⚡"),
    "3": ("icky/translate:latest", "Icky Translate - Kompakt, spezialisiert", "🔄"),
    "4": ("llama3.2:latest", "Llama 3.2 - Lokal, effizient", "🦙"),
    "5": ("mistral:latest", "Mistral - Ausgewogen", "🌪️"),
}


def get_available_model_ids() -> List[str]:
    """Return list of available model IDs."""
    return list(AVAILABLE_MODELS.keys())


def get_model_info(model_id: str) -> Tuple[str, str, str]:
    """
    Get model info by ID.
    
    Returns:
        Tuple of (model_name, description, emoji)
    """
    if model_id in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[model_id]
    # Default fallback
    return ("kimi-k2.5:cloud", "Kimik2.5 Cloud", "🧠")


def show_model_menu(agent_name: str, agent_role: str = "") -> str:
    """
    Show interactive model selection menu for an agent.
    
    Args:
        agent_name: Name of the agent
        agent_role: Optional role description
        
    Returns:
        Selected model name
    """
    title = f"🤖 Modell-Auswahl für {agent_name}"
    if agent_role:
        title += f" ({agent_role})"
    
    console.print(Panel(
        title,
        border_style="cyan",
        box=box.DOUBLE
    ))
    
    # Create table
    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED
    )
    table.add_column("#", style="bold", width=4)
    table.add_column("Modell", style="green")
    table.add_column("Beschreibung", style="dim")
    table.add_column("", style="bold")
    
    for key, (model, desc, emoji) in AVAILABLE_MODELS.items():
        table.add_row(f"[{key}]", model, desc, emoji)
    
    console.print(table)
    console.print()
    
    # Get user input
    while True:
        choice = console.input(
            f"[bold cyan]Wähle Modell für {agent_name}[/bold cyan] [1-{len(AVAILABLE_MODELS)}, ENTER=1]: "
        ).strip()
        
        if choice == "":
            choice = "1"
        
        if choice in AVAILABLE_MODELS:
            model, desc, emoji = AVAILABLE_MODELS[choice]
            console.print(f"[green]✅ {agent_name} verwendet:[/green] {emoji} {model}")
            console.print()
            return model
        
        console.print("[red]Ungültige Eingabe, bitte 1-{} wählen.[/red]".format(len(AVAILABLE_MODELS)))


def select_models_for_agents(agents: List) -> Dict[str, str]:
    """
    Let user select models for all agents.
    
    Args:
        agents: List of AgentConfig objects
        
    Returns:
        Dict mapping agent name to selected model
    """
    console.print()
    console.print(Panel(
        "[bold]⚙️  AGENTEN-KONFIGURATION[/bold]\n\n"
        "Wähle Modelle für die Agenten:\n"
        "[dim](Tipp: Verschiedene Modelle = interessantere Gespräche)[/dim]",
        border_style="blue",
        box=box.DOUBLE
    ))
    console.print()
    
    selected_models = {}
    
    for agent in agents:
        model = show_model_menu(agent.name, agent.role)
        selected_models[agent.name] = model
    
    # Show summary
    console.print(Panel(
        "[bold]📋 GEWÄHLTE KONFIGURATION:[/bold]",
        border_style="green",
        box=box.ROUNDED
    ))
    
    summary_table = Table(show_header=False, box=box.SIMPLE)
    summary_table.add_column("Agent", style="cyan")
    summary_table.add_column("Modell", style="green")
    
    for agent in agents:
        model = selected_models[agent.name]
        summary_table.add_row(f"  {agent.name}", model)
    
    console.print(summary_table)
    console.print()
    
    # Confirm
    confirm = console.input(
        "[bold]Ist das korrekt?[/bold] [j/n, ENTER=j]: "
    ).strip().lower()
    
    if confirm not in ("", "j", "ja", "y", "yes"):
        console.print("\n[yellow]Okay, starte Auswahl neu...[/yellow]\n")
        return select_models_for_agents(agents)
    
    return selected_models


def apply_models_to_agents(agents: List, model_map: Dict[str, str]) -> None:
    """
    Apply selected models to agent configurations.
    
    Args:
        agents: List of AgentConfig objects (modified in place)
        model_map: Dict mapping agent name to model
    """
    for agent in agents:
        if agent.name in model_map:
            agent.model = model_map[agent.name]


def interactive_model_selection(agents: List, skip_if_default: bool = False) -> bool:
    """
    Run interactive model selection flow.
    
    Args:
        agents: List of AgentConfig objects (modified in place)
        skip_if_default: If True, skip and use default models from JSON
        
    Returns:
        True if models were changed, False otherwise
    """
    if skip_if_default:
        console.print("[dim]Verwende Modelle aus Agenten-Konfiguration...[/dim]")
        return False
    
    # Show current models
    console.print("[dim]Aktuelle Modelle aus Konfiguration:[/dim]")
    for agent in agents:
        console.print(f"  • {agent.name}: {agent.model}")
    console.print()
    
    # Ask if user wants to change
    change = console.input(
        "[bold]Modelle anpassen?[/bold] [j/n, ENTER=j]: "
    ).strip().lower()
    
    if change in ("", "j", "ja", "y", "yes"):
        model_map = select_models_for_agents(agents)
        apply_models_to_agents(agents, model_map)
        
        console.print(Panel(
            "[bold green]✅ Modelle aktualisiert![/bold green]",
            border_style="green"
        ))
        return True
    
    return False