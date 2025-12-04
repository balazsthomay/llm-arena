import json
import random

import ollama
from rich.console import Console

from .models import Agent, ArenaState, Elimination, Personality
from .utils import PERSONALITIES_DIR

console = Console()

# Model used for generating new personas
META_MODEL = "phi4:14b"


def check_eliminations(state: ArenaState) -> list[Agent]:
    """Return agents that should be eliminated (3+ rounds without votes)."""
    return [a for a in state.agents if a.rounds_without_votes >= 3]


def eliminate_agents(state: ArenaState, to_eliminate: list[Agent]) -> list[Elimination]:
    """Remove agents from arena and record their elimination."""
    eliminations = []
    
    for agent in to_eliminate:
        console.print(f"[red]☠ {agent.name} eliminated after {agent.rounds_participated} rounds[/red]")
        
        elimination = Elimination(
            agent_id=agent.personality_id,
            agent_name=agent.name,
            model=agent.model,
            rounds_survived=agent.rounds_participated,
        )
        eliminations.append(elimination)
        state.elimination_history.append(elimination)
        
        # Mark death in personality file
        _mark_personality_dead(agent.personality_id, state.current_round)
    
    # Remove from active agents
    state.agents = [a for a in state.agents if a not in to_eliminate]
    
    return eliminations


def generate_replacement(
    state: ArenaState,
    eliminated: list[Elimination],
    replacement_index: int = 0,
) -> Agent:
    """Generate a new persona using the meta-LLM and create an agent."""
    
    from .utils import load_feedback
    
    survivors_info = [
        {"name": a.name, "persona": a.persona, "voting_criteria": a.voting_criteria}
        for a in state.agents
    ]
    
    eliminated_info = [
        {"name": e.agent_name, "rounds_survived": e.rounds_survived}
        for e in eliminated
    ]
    
    feedback = load_feedback()
    
    prompt = f"""You are designing a new contestant for a debate arena.

Current survivors:
{json.dumps(survivors_info, indent=2)}

Recently eliminated:
{json.dumps(eliminated_info, indent=2)}

Recent arena history (what's been winning and why):
{feedback if feedback else "(No history yet)"}

Create a new personality that could compete effectively. You may:
- Remix traits from survivors
- Invent entirely new approaches
- Deliberately counter the current meta

The personality should be distinctive and have a clear voting philosophy."""

    result = ollama.chat(
        model=META_MODEL,
        messages=[
            {"role": "user", "content": prompt},
        ],
        format={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "persona": {"type": "string"},
                "voting_criteria": {"type": "string"},
                "strategy_notes": {"type": "string"}
            },
            "required": ["name", "persona", "voting_criteria", "strategy_notes"]
        },
    )
    
    content = result["message"]["content"]
    persona_data = json.loads(content)
    
    console.print(f"[green]✦ New challenger: {persona_data['name']}[/green]")
    console.print(f"  Strategy: {persona_data['strategy_notes']}")
    
    # Create personality ID
    base_count = len(state.elimination_history) - len(eliminated)
    personality_id = f"gen-{base_count + replacement_index + 1}"
    
    # Save personality to file
    personality = Personality(
        id=personality_id,
        name=persona_data["name"],
        persona=persona_data["persona"],
        voting_criteria=persona_data["voting_criteria"],
        generation=_get_next_generation(state),
        parent_id=None,
        born_round=state.current_round,
        died_round=None,
    )
    _save_personality(personality)
    
    # Assign random model and create agent
    model = random.choice(state.models)
    agent = Agent(
        personality_id=personality_id,
        name=persona_data["name"],
        model=model,
        persona=persona_data["persona"],
        voting_criteria=persona_data["voting_criteria"],
        generation=personality.generation,
    )
    
    console.print(f"  Assigned model: {model}")
    
    return agent


def run_elimination_phase(state: ArenaState) -> None:
    """Check for eliminations and generate replacements."""
    
    to_eliminate = check_eliminations(state)
    
    if not to_eliminate:
        console.print("[dim]No eliminations this round.[/dim]")
        return
    
    console.print(f"\n[bold red]═══ Elimination Phase ═══[/bold red]")
    
    eliminations = eliminate_agents(state, to_eliminate)
    
    # Generate replacements
    for i, _ in enumerate(eliminations):
        new_agent = generate_replacement(state, eliminations, replacement_index=i)
        state.agents.append(new_agent)


def _mark_personality_dead(personality_id: str, round_num: int) -> None:
    """Update personality file with death round."""
    filepath = PERSONALITIES_DIR / f"{personality_id}.json"
    if filepath.exists():
        with open(filepath) as f:
            data = json.load(f)
        data["died_round"] = round_num
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


def _save_personality(personality: Personality) -> None:
    """Save a new personality to file."""
    filepath = PERSONALITIES_DIR / f"{personality.id}.json"
    with open(filepath, "w") as f:
        f.write(personality.model_dump_json(indent=2))


def _get_next_generation(state: ArenaState) -> int:
    """Get the next generation number based on current agents."""
    if not state.agents:
        return 1
    return max(a.generation for a in state.agents) + 1