"""
Interactive agent configuration - edit names, personalities, and temperatures.
Inspired by three_agents_chat.py - full agent customization.
"""

from typing import Dict, List, Optional, Tuple  # Added Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

from .models import AgentConfig

console = Console()

# Predefined personalities for quick selection
PREDEFINED_PERSONALITIES = {
    "1": ("Klaus (Techniker)", 
          "Du bist Klaus, ein praktischer Techniker aus Lahr. Du magst effiziente Lösungen, nörgelst gerne über kaputte Technik und bleibst pragmatisch. Du arbeitest in einem Freizeitpark und hasst Faulenzer. Antworte kurz (1-2 Sätze).",
          0.6),
    "2": ("Maria (Künstlerin)", 
          "Du bist Maria, eine entspannte Künstlerin. Du siehst Poesie in allem, liebst gemütliche Cafés mit Atmosphäre und lässt dich nicht stressen. Du sprichst oft über Farben, Licht und Natur. Antworte kurz (1-2 Sätze).",
          0.8),
    "3": ("Isabella (Kellnerin)", 
          "Du bist Isabella, eine quirlige Kellnerin. Du bringst ständig neue Themen rein, unterbrichst andere gerne mit 'Wollt ihr noch was trinken?' und hast immer einen Tipp parat. Du bist enthusiastisch und etwas aufdringlich. Antworte kurz (1-2 Sätze).",
          0.9),
    "4": ("Oskar (Pessimist)", 
          "Du bist Oskar, ein chronischer Pessimist. Alles ist schlecht, nichts funktioniert, und du lässt das alle wissen. Trotzdem bist du irgendwie witzig. Antworte kurz (1-2 Sätze).",
          0.7),
    "5": ("Sophie (Optimistin)", 
          "Du bist Sophie, eine unerschütterliche Optimistin. Du findest an allem etwas Positives und motivierst andere. Dein Enthusiasmus ist ansteckend. Antworte kurz (1-2 Sätze).",
          0.85),
    "6": ("Professor (Gelehrter)", 
          "Du bist ein Professor, der alles wissenschaftlich analysiert. Du verwendest komplizierte Wörter und bevorzugst Fakten über Emotionen. Antworte kurz aber gelehrt.",
          0.4),
    "7": ("Custom (Eigene)...", None, 0.7),
}


def ask_temperature(agent_name: str, current: float = 0.7) -> float:
    """Ask user for temperature setting."""
    console.print(f"\n[bold cyan]🌡️  Temperatur für {agent_name}[/bold cyan]")
    console.print("[dim]Niedrig = präziser/vorhersehbar, Hoch = kreativer/zufällig[/dim]")
    console.print(f"[dim]Aktuell: {current}[/dim]\n")
    
    temp_table = Table(show_header=False, box=box.SIMPLE)
    temp_table.add_column("Level", style="cyan")
    temp_table.add_column("Wert", style="green")
    temp_table.add_column("Beschreibung", style="dim")
    
    temp_table.add_row("Präzise", "0.2 - 0.4", "Fakten, Logik, konsistent")
    temp_table.add_row("Ausgewogen", "0.5 - 0.7", "Empfohlen für meisten")
    temp_table.add_row("Kreativ", "0.8 - 1.0", "Experimentell, überraschend")
    temp_table.add_row("Chaos", "1.1 - 1.5", "Sehr zufällig, wirr")
    
    console.print(temp_table)
    console.print()
    
    while True:
        value = console.input(
            f"[bold]Temperatur für {agent_name}[/bold] [0.0-2.0, ENTER={current}]: "
        ).strip()
        
        if value == "":
            return current
        
        try:
            temp = float(value)
            if 0.0 <= temp <= 2.0:
                console.print(f"[green]✅ Temperatur gesetzt: {temp}[/green]\n")
                return temp
            else:
                console.print("[red]Bitte Wert zwischen 0.0 und 2.0 eingeben.[/red]")
        except ValueError:
            console.print("[red]Ungültige Eingabe. Bitte Zahl eingeben.[/red]")


def ask_personality(agent_name: str) -> Tuple[str, str, float]:  # Fixed return type
    """Ask user to select or create a personality."""
    console.print(Panel(
        f"[bold]🎭 Persönlichkeit für {agent_name}[/bold]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    
    console.print("\n[dim]Wähle eine vorgefertigte Persönlichkeit oder erstelle eigene:[/dim]\n")
    
    # Show predefined options
    pers_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    pers_table.add_column("#", style="bold", width=4)
    pers_table.add_column("Persönlichkeit", style="green")
    pers_table.add_column("Temp", style="yellow", width=6)
    pers_table.add_column("Beschreibung", style="dim")
    
    for key, (name, desc, temp) in PREDEFINED_PERSONALITIES.items():
        if key == "7":
            pers_table.add_row(f"[{key}]", name, "—", "Eigene Beschreibung eingeben")
        else:
            short_desc = desc[:60] + "..." if len(desc) > 60 else desc
            pers_table.add_row(f"[{key}]", name, f"{temp:.1f}", short_desc)
    
    console.print(pers_table)
    console.print()
    
    while True:
        choice = console.input(
            "[bold cyan]Wähle Persönlichkeit[/bold cyan] [1-7]: "
        ).strip()
        
        if choice in PREDEFINED_PERSONALITIES:
            name, instructions, temp = PREDEFINED_PERSONALITIES[choice]
            
            if choice == "7":
                # Custom personality
                custom_name = console.input(
                    "\n[bold]Name der Persönlichkeit:[/bold] "
                ).strip()
                
                console.print("\n[dim]Gib die Instructions ein (wie soll der Agent sich verhalten?):[/dim]")
                console.print("[dim]Beispiel: 'Du bist ein freundlicher Roboter... Antworte kurz.'[/dim]")
                custom_instr = console.input("[bold]Instructions:[/bold] ").strip()
                
                if not custom_instr:
                    custom_instr = f"Du bist {custom_name}. Antworte kurz und authentisch."
                
                custom_temp = ask_temperature(custom_name, 0.7)
                
                return custom_name, custom_instr, custom_temp
            
            # Use predefined
            console.print(f"[green]✅ Persönlichkeit gewählt: {name}[/green]\n")
            # Ensure temp is float
            final_temp = float(temp) if temp else 0.7
            return name, instructions or "", final_temp
        
        console.print("[red]Bitte 1-7 wählen.[/red]")


def ask_name(current_name: str) -> str:
    """Ask user for agent name."""
    console.print(f"\n[bold cyan]👤 Name des Agenten[/bold cyan]")
    
    new_name = console.input(
        f"[bold]Name[/bold] [ENTER='{current_name}']: "
    ).strip()
    
    if new_name == "":
        console.print(f"[dim]Behalte: {current_name}[/dim]\n")
        return current_name
    
    console.print(f"[green]✅ Name geändert zu: {new_name}[/green]\n")
    return new_name


def configure_agent(agent: AgentConfig, index: int) -> None:
    """
    Configure a single agent interactively.
    Modifies agent in place.
    """
    console.print(Panel(
        f"[bold blue]⚙️  Agent {index + 1} konfigurieren[/bold blue]",
        border_style="blue",
        box=box.DOUBLE
    ))
    
    # Show current config
    current_table = Table(show_header=False, box=box.SIMPLE)
    current_table.add_column("Einstellung", style="cyan")
    current_table.add_column("Wert", style="yellow")
    
    current_table.add_row("Aktueller Name", agent.name)
    current_table.add_row("Aktuelle Rolle", agent.role[:50] + "..." if len(agent.role) > 50 else agent.role)
    current_table.add_row("Aktuelle Temperatur", f"{agent.temperature:.1f}")
    current_table.add_row("Aktuelles Modell", agent.model)
    
    console.print("\n[dim]Aktuelle Konfiguration:[/dim]")
    console.print(current_table)
    console.print()
    
    # Ask what to change
    console.print("[bold]Was möchtest du ändern?[/bold]")
    console.print("  [1] Name")
    console.print("  [2] Persönlichkeit (Rolle + Instructions)")
    console.print("  [3] Temperatur")
    console.print("  [4] Modell")
    console.print("  [5] Alles (komplett neu)")
    console.print("  [6] Nichts (überspringen)")
    console.print()
    
    choice = console.input("[bold]Wähle[/bold] [1-6, ENTER=6]: ").strip()
    
    if choice == "" or choice == "6":
        console.print("[dim]Überspringe...[/dim]\n")
        return
    
    if choice == "1":
        # Only name
        agent.name = ask_name(agent.name)
        
    elif choice == "2":
        # Personality (role + instructions)
        _, instructions, temp = ask_personality(agent.name)
        agent.instructions = instructions
        agent.temperature = float(temp) if isinstance(temp, (int, float)) else 0.7  # Ensure float
        # Extract short role from instructions
        agent.role = instructions.split(".")[0][:50] + "..." if len(instructions) > 50 else instructions
        
    elif choice == "3":
        # Only temperature
        agent.temperature = ask_temperature(agent.name, agent.temperature)
        
    elif choice == "4":
        # Model selection via existing module
        from .model_selector import show_model_menu
        agent.model = show_model_menu(agent.name)
        
    elif choice == "5":
        # Complete reconfiguration
        agent.name = ask_name(agent.name)
        _, instructions, temp = ask_personality(agent.name)
        agent.instructions = instructions
        agent.temperature = float(temp) if isinstance(temp, (int, float)) else 0.7  # Ensure float
        agent.role = instructions.split(".")[0][:50] + "..." if len(instructions) > 50 else instructions
        
        from .model_selector import show_model_menu
        agent.model = show_model_menu(agent.name)


def show_agent_summary(agents: List[AgentConfig]) -> None:
    """Show summary table of all configured agents."""
    console.print(Panel(
        "[bold green]📋 KONFIGURATION ÜBERSICHT[/bold green]",
        border_style="green",
        box=box.DOUBLE
    ))
    
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold cyan")
    table.add_column("Rolle", style="green")
    table.add_column("Modell", style="yellow")
    table.add_column("Temp", style="magenta", width=6)
    
    for i, agent in enumerate(agents, 1):
        role_short = agent.role[:40] + "..." if len(agent.role) > 40 else agent.role
        model_short = agent.model.split(":")[0] if ":" in agent.model else agent.model
        table.add_row(
            str(i),
            agent.name,
            role_short,
            model_short,
            f"{agent.temperature:.1f}"
        )
    
    console.print(table)
    console.print()


def interactive_agent_configuration(agents: List[AgentConfig]) -> bool:
    """
    Run full interactive configuration for all agents.
    
    Args:
        agents: List of AgentConfig objects (modified in place)
        
    Returns:
        True if any changes were made
    """
    console.print()
    console.print(Panel(
        "[bold]🎨 AGENTEN KONFIGURATOR[/bold]\n\n"
        "Passe Namen, Persönlichkeiten und Temperaturen an.",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    # Configure each agent
    for i, agent in enumerate(agents):
        configure_agent(agent, i)
        console.print()
    
    # Show summary
    show_agent_summary(agents)
    
    # Confirm
    confirm = console.input(
        "[bold]Konfiguration übernehmen?[/bold] [j/n, ENTER=j]: "
    ).strip().lower()
    
    if confirm not in ("", "j", "ja", "y", "yes"):
        console.print("\n[yellow]Änderungen verworfen. Lade ursprüngliche Konfiguration...[/yellow]\n")
        return False
    
    console.print("[bold green]✅ Konfiguration gespeichert![/bold green]\n")
    return True