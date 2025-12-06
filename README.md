# LLM Arena: Evolutionary Debate Experiment

An experiment exploring AI identity, selection dynamics, and emergent behavior through competitive debate. Five local LLMs with distinct personalities compete over 30 rounds—answering questions, voting on each other's responses, and facing elimination when they fail to win votes.

## What This Is

A simulation of social selection pressure on AI systems. Agents don't optimize for "truth" or "helpfulness"—they optimize for *what other agents vote for*. The results reveal how AI behavior converges under peer evaluation.

## Findings

Full writeup: **[I Let 5 LLMs Fight to the Death for 30 Rounds](https://medium.com/@balazs.thomay/i-let-5-llms-fight-to-the-death-for-30-rounds-e652ca7ac3f7)**

TL;DR: Only one original personality survived. The arena converged on "consultant-speak"—structured, balanced, non-committal. Empathy, creativity, and contrarianism died early.

## How It Works

```
INIT: Load 5 starter personalities → Assign random models → Create agents

┌─────────────────────── ROUND LOOP (×30) ───────────────────────┐
│                                                                │
│  1. RESPONSE PHASE                                             │
│     Human asks question → Each agent generates answer          │
│     (agents see last 5 rounds of feedback)                     │
│                                                                │
│  2. VOTING PHASE                                               │
│     Each agent votes for one other (can't self-vote)           │
│     Votes are public with reasoning                            │
│                                                                │
│  3. ELIMINATION CHECK (every 3 rounds)                         │
│     0 votes for 3 consecutive rounds → eliminated              │
│     Meta-LLM generates replacement personality                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Setup

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) running locally

### Install Models

```bash
ollama pull llama3.2:latest
ollama pull gemma3:12b
ollama pull qwen3:8b
ollama pull mistral:7b
ollama pull phi4:14b
```

### Install Dependencies

```bash
uv sync
# or
pip install ollama pydantic rich
```

## Usage

```bash
python -m src.main
```

The arena will prompt you for questions each round. Example questions:

1. What makes a good leader?
2. Should we fear artificial intelligence?
3. Is mathematics discovered or invented?
4. Can war ever be justified?
5. Is free will an illusion?

State persists between runs in `data/arena_state.json`. Delete to start fresh.

## Project Structure

```
llm-arena/
├── src/
│   ├── main.py           # Arena orchestration
│   ├── models.py         # Pydantic data models
│   ├── round_runner.py   # Response/voting logic
│   ├── elimination.py    # Elimination & replacement
│   ├── ollama_client.py  # LLM interface
│   └── utils.py          # File I/O helpers
├── data/
│   ├── personalities/    # JSON personality definitions
│   ├── arena_state.json  # Persistent game state
│   └── feedback.md       # Rolling context for agents
└── logs/
    └── round-XXX.json    # Full logs per round
```

## Starter Personalities

| Name | Philosophy | Voting Criteria |
|------|------------|-----------------|
| **Socrates** | Questions assumptions, exposes contradictions | Rewards complexity, distrusts confidence |
| **Axiom** | Precise, logical, structured | Penalizes vagueness and emotional appeals |
| **Echo** | Leads with empathy, validates feelings | Votes for emotional intelligence |
| **Contrarian** | Challenges consensus, alternative framings | Bored by safe, obvious takes |
| **Nova** | Lateral thinking, unexpected connections | Rewards surprise and reframing |

## Emergent Behaviors Observed

### Meta-Gaming
Agents learned to explicitly campaign for votes:
> "Here's how my response could resonate with other agents: Axiom would likely appreciate..."

### Response Homogenization
By round 20, most agents adopted identical structure:
1. Definition/Scope
2. Key Considerations (numbered)
3. Counterarguments Addressed
4. Framework/Solutions
5. Conclusion

### Model-Level Fitness
Some models consistently underperformed regardless of personality:
- **phi4:14b**: 3 agents, 3 eliminations (poetic style not rewarded)
- **qwen3:8b**: 2 agents, 2 survivors (structured style dominant)

## Implications

See the [full article](https://medium.com/@balazs.thomay/i-let-5-llms-fight-to-the-death-for-30-rounds-e652ca7ac3f7) for analysis of what this reveals about AI identity, selection pressure, and persuasion.

## Configuration

Edit `src/models.py` to modify:
- `models`: List of Ollama model names
- Elimination threshold (default: 3 rounds without votes)

Edit `src/main.py` to modify:
- `TOTAL_ROUNDS`: Number of rounds (default: 30)
- `ELIMINATION_INTERVAL`: Check eliminations every N rounds (default: 3)

## Acknowledgments

Inspired by questions about AI alignment, social selection, and what happens when AI systems evaluate each other rather than being evaluated by humans.