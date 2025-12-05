#!/usr/bin/env python3
"""
Simple interactive script to use Zazu Parliament
Run: python3 examples/simple_usage.py
"""

import asyncio
from core.chorus import Chorus
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()


async def main():
    console.print("\n[bold cyan]🎭 Zazu Parliamentary Intelligence[/]\n")
    console.print("[dim]Type 'quit' to exit[/]\n")
    
    # Initialize parliament
    console.print("[yellow]Initializing parliament...[/]")
    chorus = Chorus()
    await chorus.initialize()
    console.print("[green]✓ Parliament ready[/]\n")
    
    try:
        while True:
            # Get user input
            user_input = Prompt.ask("[bold cyan]You[/]")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Process request
            console.print("[dim]Parliament deliberating...[/]")
            result = await chorus.process_request(user_input, mode="auto")
            
            # Display results
            console.print(Panel(
                f"[green]Mode:[/] {result['mode_used']}\n"
                f"[green]Agents:[/] {', '.join(result['agents_involved'])}\n"
                f"[green]Coherence:[/] {result['reflection']['coherence_score']:.2f}",
                title="Parliament Response",
                border_style="cyan"
            ))
            
            # Show specific outputs
            if 'artisan' in result.get('outputs', {}):
                creation = result['outputs']['artisan']['creation']
                console.print(f"\n[bold]Artisan says:[/]")
                console.print(Panel(creation['content'][:500] + "...", border_style="magenta"))
            
            if 'strategist' in result.get('outputs', {}):
                strategy = result['outputs']['strategist']['strategy']
                console.print(f"\n[bold]Strategist suggests:[/] {strategy['primary_approach']}")
            
            if 'ledger' in result.get('outputs', {}):
                analysis = result['outputs']['ledger']['analysis']
                console.print(f"\n[bold]Ledger assessed risk:[/] {analysis['risk_score']:.2f}")
            
            console.print()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/]")
    
    finally:
        console.print("\n[yellow]Shutting down parliament...[/]")
        await chorus.shutdown()
        console.print("[green]✓ Goodbye![/]\n")


if __name__ == "__main__":
    asyncio.run(main())
