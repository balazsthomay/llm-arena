from collections import defaultdict

from rich.console import Console
from rich.panel import Panel

from .models import Agent, ArenaState, Response, RoundResult, Vote
from .ollama_client import generate_response, generate_vote
from .utils import load_feedback

console = Console()


def run_round(state: ArenaState, question: str) -> RoundResult:
    """Run a complete round: collect responses, collect votes, update stats."""
    
    state.current_round += 1
    round_num = state.current_round
    feedback = load_feedback()
    
    console.print(f"\n[bold blue]═══ Round {round_num} ═══[/bold blue]")
    console.print(f"[yellow]Question:[/yellow] {question}\n")
    
    # Phase 1: Collect responses
    console.print("[bold]Phase 1: Collecting responses...[/bold]")
    responses: list[Response] = []
    for agent in state.agents:
        console.print(f"  {agent.name} ({agent.model}) thinking...")
        response = generate_response(agent, question, feedback)
        responses.append(response)
        console.print(Panel(response.content, title=f"{agent.name}", border_style="green"))
    
    # Phase 2: Collect votes
    console.print("\n[bold]Phase 2: Collecting votes...[/bold]")
    votes: list[Vote] = []
    for agent in state.agents:
        console.print(f"  {agent.name} voting...")
        vote = generate_vote(agent, question, responses, feedback)
        votes.append(vote)
        console.print(f"    → {agent.name} votes for [cyan]{vote.voted_for_name}[/cyan]: {vote.reasoning}")
    
    # Phase 3: Tally votes
    vote_tally: dict[str, int] = defaultdict(int)
    for vote in votes:
        vote_tally[vote.voted_for_id] += 1
    
    # Phase 4: Update agent stats
    for agent in state.agents:
        agent.rounds_participated += 1
        votes_received = vote_tally.get(agent.personality_id, 0)
        agent.total_votes_received += votes_received
        
        if votes_received > 0:
            agent.rounds_without_votes = 0
        else:
            agent.rounds_without_votes += 1
    
    # Display results
    console.print("\n[bold]Vote Tally:[/bold]")
    for agent in state.agents:
        votes_received = vote_tally.get(agent.personality_id, 0)
        drought = agent.rounds_without_votes
        drought_warning = " [red]⚠ ELIMINATION WARNING[/red]" if drought >= 2 else ""
        console.print(f"  {agent.name}: {votes_received} votes (drought: {drought}){drought_warning}")
    
    return RoundResult(
        round_number=round_num,
        question=question,
        responses=responses,
        votes=votes,
        vote_tally=dict(vote_tally),
    )