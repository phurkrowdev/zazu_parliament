#!/usr/bin/env python3
"""
Demo: Zazu Parliamentary Intelligence System
Shows all 7 agents working together on a complex request
"""

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chorus import Chorus
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


async def demo_inquiry():
    """Demo: Simple inquiry mode"""
    console.print("\n" + "="*70, style="bold blue")
    console.print("DEMO 1: INQUIRY MODE", style="bold blue")
    console.print("="*70 + "\n", style="bold blue")
    
    chorus = Chorus()
    await chorus.initialize()
    
    try:
        question = "What is the current system status?"
        console.print(f"[bold cyan]User:[/] {question}\n")
        
        result = await chorus.process_request(question, mode="inquiry")
        
        console.print(Panel(
            f"[green]Mode:[/] {result['mode_used']}\n"
            f"[green]Agents Involved:[/] {', '.join(result['agents_involved'])}\n"
            f"[green]Coherence Score:[/] {result['reflection']['coherence_score']:.2f}",
            title="Parliament Response",
            border_style="green"
        ))
        
    finally:
        await chorus.shutdown()


async def demo_creation():
    """Demo: Creation mode with multiple agents"""
    console.print("\n" + "="*70, style="bold magenta")
    console.print("DEMO 2: CREATION MODE (Multi-Agent Collaboration)", style="bold magenta")
    console.print("="*70 + "\n", style="bold magenta")
    
    chorus = Chorus()
    await chorus.initialize()
    
    try:
        request = "Create a mythos about the Zazu Parliament and plan how we would expand it"
        console.print(f"[bold cyan]User:[/] {request}\n")
        
        result = await chorus.process_request(request, mode="creation")
        
        console.print(Panel(
            f"[green]Mode:[/] {result['mode_used']}\n"
            f"[green]Agents Involved:[/] {', '.join(result['agents_involved'])}",
            title="Parliament Coordination",
            border_style="magenta"
        ))
        
        # Show outputs from each agent
        if 'strategist' in result['outputs']:
            strategy = result['outputs']['strategist']['strategy']
            console.print("\n[bold yellow]📋 Strategist Output:[/]")
            console.print(f"  Primary Approach: {strategy['primary_approach']}")
            console.print(f"  Timeline Phases: {len(strategy['timeline'])}")
            console.print(f"  Risk Factors: {len(strategy['risk_factors'])}")
        
        if 'artisan' in result['outputs']:
            creation = result['outputs']['artisan']['creation']
            console.print(f"\n[bold yellow]🎨 Artisan Output:[/]")
            console.print(Panel(
                Markdown(creation['content']),
                title=creation['title'],
                border_style="yellow"
            ))
        
        if 'ledger' in result['outputs']:
            analysis = result['outputs']['ledger']['analysis']
            console.print(f"\n[bold yellow]📊 Ledger Output:[/]")
            console.print(f"  Risk Score: {analysis['risk_score']:.2f}")
            console.print(f"  Risk Level: {analysis.get('risk_level', 'N/A')}")
        
        # Show Mirror reflection
        console.print(f"\n[bold blue]🪞 Mirror Reflection:[/]")
        console.print(f"  Coherence: {result['reflection']['coherence_score']:.2f}")
        console.print(f"  Emotional Load: {result['reflection']['emotional_load_estimate']}")
        console.print(f"  Progress: {result['reflection']['progress_assessment']}")
        
    finally:
        await chorus.shutdown()


async def demo_consensus():
    """Demo: Consensus mechanism with multiple agent perspectives"""
    console.print("\n" + "="*70, style="bold green")
    console.print("DEMO 3: CONSENSUS MODE (Redundant Epistemics)", style="bold green")
    console.print("="*70 + "\n", style="bold green")
    
    chorus = Chorus()
    await chorus.initialize()
    
    try:
        question = "Should we proceed with Phase 3 of Zazu development?"
        console.print(f"[bold cyan]User:[/] {question}\n")
        
        result = await chorus.process_request(
            question,
            mode="creation",
            require_consensus=True
        )
        
        console.print(Panel(
            f"[green]Agents Consulted:[/] {', '.join(result['agents_involved'])}\n"
            f"[green]Consensus Score:[/] {result.get('consensus', {}).get('consensus_score', 0):.2f}\n"
            f"[green]Threshold Met:[/] {result.get('consensus', {}).get('threshold_met', False)}",
            title="Multi-Agent Consensus",
            border_style="green"
        ))
        
        if 'consensus' in result:
            console.print("\n[bold]Additional Perspectives:[/]")
            for perspective in result['consensus'].get('additional_perspectives', []):
                console.print(f"  • {perspective['agent']}: consulted")
        
    finally:
        await chorus.shutdown()


async def demo_full_workflow():
    """Demo: Complete workflow showing all agent types"""
    console.print("\n" + "="*70, style="bold red")
    console.print("DEMO 4: FULL WORKFLOW (All 7 Agents)", style="bold red")
    console.print("="*70 + "\n", style="bold red")
    
    chorus = Chorus()
    await chorus.initialize()
    
    try:
        # Show agent status
        status = chorus.get_agent_status()
        console.print("[bold]Parliament Status:[/]")
        for agent, active in status.items():
            status_icon = "✅" if active else "❌"
            console.print(f"  {status_icon} {agent.title()}")
        
        console.print("\n[bold cyan]User:[/] Let's plan the next phase of Zazu, create a mythos" 
                     " about it, assess the risks, and reflect on our readiness.\n")
        
        result = await chorus.process_request(
            "Plan Phase 3 of Zazu, create a mythos about parliamentary evolution, "
            "and assess implementation risks",
            mode="creation",
            require_consensus=True
        )
        
        console.print(Panel(
            f"[green]Total Agents Involved:[/] {len(result['agents_involved'])}/7\n"
            f"[green]Agents:[/] {', '.join(result['agents_involved'])}\n"
            f"[green]Mode:[/] {result['mode_used']}\n"
            f"[green]Consensus Reached:[/] {result.get('consensus', {}).get('threshold_met', 'N/A')}",
            title="🎭 Parliamentary Intelligence - Full Coordination",
            border_style="red"
        ))
        
        # Final coherence assessment
        coherence = result['reflection']['coherence_score']
        coherence_color = "green" if coherence > 0.7 else "yellow" if coherence > 0.5 else "red"
        
        console.print(f"\n[bold {coherence_color}]Final Coherence Score: {coherence:.2f}[/]")
        console.print(f"[dim]{result['reflection']['progress_assessment']}[/]")
        
    finally:
        await chorus.shutdown()


async def main():
    console.print("\n" + "="*70, style="bold white")
    console.print("  ZAZU PARLIAMENTARY INTELLIGENCE SYSTEM - LIVE DEMO", style="bold white")
    console.print("  7-Agent Constitutional Multi-Agent System", style="bold white")
    console.print("="*70 + "\n", style="bold white")
    
    try:
        # Run all demos
        await demo_inquiry()
        await asyncio.sleep(1)
        
        await demo_creation()
        await asyncio.sleep(1)
        
        await demo_consensus()
        await asyncio.sleep(1)
        
        await demo_full_workflow()
        
        console.print("\n" + "="*70, style="bold green")
        console.print("  ✅ ALL DEMOS COMPLETE", style="bold green")
        console.print("  The Zazu Parliament is fully operational!", style="bold green")
        console.print("="*70 + "\n", style="bold green")
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
