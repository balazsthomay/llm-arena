from datetime import datetime
from pydantic import BaseModel, Field


class Personality(BaseModel):
    """Loaded from personality JSON files."""
    id: str
    name: str
    model: str | None = None  # Assigned at contestant creation
    persona: str
    voting_criteria: str
    generation: int = 0
    parent_id: str | None = None
    born_round: int = 0
    died_round: int | None = None


class Agent(BaseModel):
    """A personality paired with a model, actively competing."""
    personality_id: str
    name: str
    model: str
    persona: str
    voting_criteria: str
    generation: int
    
    # Runtime stats
    total_votes_received: int = 0
    rounds_without_votes: int = 0  # Reset to 0 when they get a vote
    rounds_participated: int = 0


class Response(BaseModel):
    """One contestant's answer to a question."""
    contestant_id: str
    contestant_name: str
    model: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Vote(BaseModel):
    """A single vote from one contestant to another."""
    voter_id: str
    voter_name: str
    voted_for_id: str
    voted_for_name: str
    reasoning: str | None = None  # Why they voted this way


class RoundResult(BaseModel):
    round_number: int
    question: str
    responses: list[Response]
    votes: list[Vote]
    vote_tally: dict[str, int]  # agent_id -> vote count this round
    timestamp: datetime = Field(default_factory=datetime.now)


class Elimination(BaseModel):
    """Record of an eliminated contestant."""
    contestant_id: str
    contestant_name: str
    model: str
    generation: int
    eliminated_round: int
    total_votes_received: int
    rounds_survived: int


class ArenaState(BaseModel):
    """Full game state, persisted between runs."""
    current_round: int = 0
    contestants: list[Agent] = []
    models: list[str] = [
        "llama3.2:latest",
        "gemma3:12b",
        "qwen3:8b",
        "mistral:7b",
        "phi4:14b"
    ]
    elimination_history: list[Elimination] = []