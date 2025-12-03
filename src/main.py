import random

from rich.console import Console

from .elimination import run_elimination_phase
from .models import ArenaState, RoundResult
from .round_runner import run_round
from .utils import (
    create_agents,
    load_personalities,
    load_state,
    save_feedback,
    save_round_log,
    save_state,
)

console = Console()

TOTAL_ROUNDS = 30
ELIMINATION_INTERVAL = 3  # Check eliminations every N rounds


def initialize_arena() -> ArenaState:
    """Initialize a fresh arena with 5 agents."""
    console.print("[bold]Initializing Arena...[/bold]")
    
    state = ArenaState()
    personalities = load_personalities()
    
    # Filter to starter personalities only
    starters = [p for p in personalities if p.id.startswith("starter-")]
    
    if len(starters) < 5:
        raise ValueError(f"Need 5 starter personalities, found {len(starters)}")
    
    state.agents = create_agents(starters[:5], state.models)
    
    console.print("\n[bold]Agents:[/bold]")
    for agent in state.agents:
        console.print(f"  {agent.name} → {agent.model}")
    
    return state


def build_round_summary(result: RoundResult, state: ArenaState) -> str:
    """Build a summary string for the feedback file."""
    
    # Vote counts
    vote_parts = []
    for agent in state.agents:
        count = result.vote_tally.get(agent.personality_id, 0)
        vote_parts.append(f"{agent.name}→{count}")
    votes_str = ", ".join(vote_parts)
    
    # Who voted for whom
    voting_record = []
    for vote in result.votes:
        voting_record.append(f"{vote.voter_name}→{vote.voted_for_name}")
    voting_str = ", ".join(voting_record)
    
    summary = f"""## Round {result.round_number}
Question: {result.question}
Votes: {votes_str}
Voting record: {voting_str}
"""
    return summary


def run_arena(questions: list[str] | None = None) -> None:
    """Run the full arena for TOTAL_ROUNDS."""
    
    # Try to resume existing state, or initialize fresh
    state = load_state()
    if not state.agents:
        state = initialize_arena()
    
    console.print(f"\n[bold green]Starting Arena — {TOTAL_ROUNDS} rounds[/bold green]\n")
    
    rounds_to_run = TOTAL_ROUNDS - state.current_round
    
    for i in range(rounds_to_run):
        # Get question
        if questions and i < len(questions):
            question = questions[i]
        else:
            question = console.input("\n[yellow]Enter question for this round:[/yellow] ")
        
        # Run round
        result = run_round(state, question)
        
        # Build and save feedback
        summary = build_round_summary(result, state)
        save_feedback(summary)
        
        # Save round log
        save_round_log(result.model_dump(), result.round_number)
        
        # Check eliminations every N rounds
        if state.current_round % ELIMINATION_INTERVAL == 0:
            run_elimination_phase(state)
        
        # Save state after each round
        save_state(state)
        
        console.print(f"\n[dim]Round {state.current_round} complete. State saved.[/dim]")
    
    console.print("\n[bold green]Arena complete![/bold green]")
    show_final_stats(state)


def show_final_stats(state: ArenaState) -> None:
    """Display final arena statistics."""
    
    console.print("\n[bold]═══ Final Stats ═══[/bold]")
    
    console.print("\n[bold]Surviving Agents:[/bold]")
    for agent in state.agents:
        console.print(f"  {agent.name} ({agent.model})")
        console.print(f"    Total votes: {agent.total_votes_received}")
        console.print(f"    Rounds survived: {agent.rounds_participated}")
    
    console.print(f"\n[bold]Total Eliminations:[/bold] {len(state.elimination_history)}")
    for e in state.elimination_history:
        console.print(f"  {e.agent_name} ({e.model}) — survived {e.rounds_survived} rounds")


if __name__ == "__main__":
    run_arena()