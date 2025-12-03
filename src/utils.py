import json
import random
from pathlib import Path

from .models import Agent, ArenaState, Personality


# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PERSONALITIES_DIR = DATA_DIR / "personalities"
STATE_FILE = DATA_DIR / "arena_state.json"
FEEDBACK_FILE = DATA_DIR / "feedback.md"
LOGS_DIR = Path(__file__).parent.parent / "logs"


def load_personalities() -> list[Personality]:
    """Load all personality JSON files from data/personalities/"""
    personalities = []
    for file in PERSONALITIES_DIR.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            personalities.append(Personality(**data))
    return personalities


def create_agents(personalities: list[Personality], models: list[str]) -> list[Agent]:
    """Pair personalities with randomly assigned models."""
    shuffled_models = models.copy()
    random.shuffle(shuffled_models)
    
    agents = []
    for i, personality in enumerate(personalities):
        model = shuffled_models[i % len(shuffled_models)]
        agent = Agent(
            personality_id=personality.id,
            name=personality.name,
            model=model,
            persona=personality.persona,
            voting_criteria=personality.voting_criteria,
            generation=personality.generation,
        )
        agents.append(agent)
    return agents


def save_state(state: ArenaState) -> None:
    """Persist arena state to JSON."""
    with open(STATE_FILE, "w") as f:
        f.write(state.model_dump_json(indent=2))


def load_state() -> ArenaState:
    """Load arena state from JSON, or return fresh state if not found."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            data = json.load(f)
            return ArenaState(**data)
    return ArenaState()


def load_feedback() -> str:
    """Load the feedback file contents."""
    if FEEDBACK_FILE.exists():
        return FEEDBACK_FILE.read_text()
    return ""


def save_feedback(new_round_summary: str, max_rounds: int = 5) -> None:
    """Append new round summary, keep only last N rounds."""
    
    # Load existing summaries
    summaries = []
    if FEEDBACK_FILE.exists():
        content = FEEDBACK_FILE.read_text()
        parts = content.split("## Round ")
        summaries = [f"## Round {p}" for p in parts[1:] if p.strip()]
    
    # Append new summary
    summaries.append(new_round_summary)
    
    # Keep only last N
    summaries = summaries[-max_rounds:]
    
    # Write back
    header = "# Arena Feedback\n\nRecent voting patterns and eliminations.\n\n"
    FEEDBACK_FILE.write_text(header + "\n".join(summaries))


def save_round_log(round_result: dict, round_number: int) -> None:
    """Save a round's complete log to logs/round-XXX.json"""
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"round-{round_number:03d}.json"
    with open(log_file, "w") as f:
        json.dump(round_result, f, indent=2, default=str)