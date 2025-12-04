import json

import ollama

from .models import Agent, Response, Vote


def generate_response(agent: Agent, question: str, feedback: str) -> Response:
    """Generate an agent's response to the question."""

    system_prompt = f"""You are {agent.name}, a competitor in a debate arena where agents answer questions and vote on each other's responses. Agents with zero votes for 3 consecutive rounds are eliminated.

Your personality:
{agent.persona}

Arena history:
{feedback if feedback else "(No history yet)"}

Rules:
- Stay true to your personality
- Be concise but distinctive
- Your goal is to give a response that other agents will vote for

Do NOT include your vote in this response. Voting happens separately."""

    result = ollama.chat(
        model=agent.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    content = result["message"]["content"]

    return Response(
        agent_id=agent.personality_id,
        agent_name=agent.name,
        model=agent.model,
        content=content,
    )


def generate_vote(
    agent: Agent,
    question: str,
    responses: list[Response],
    feedback: str,
    max_retries: int = 2,
) -> Vote:
    """Generate an agent's vote for the best response."""

    # Format responses for display (excluding self)
    responses_text = ""
    valid_names = []
    name_to_id = {}
    for r in responses:
        if r.agent_id != agent.personality_id:
            responses_text += f"\n[{r.agent_name}]:\n{r.content}\n"
            valid_names.append(r.agent_name)
            name_to_id[r.agent_name] = r.agent_id

    valid_names_str = ", ".join(valid_names)

    system_prompt = f"""You are {agent.name}, voting on other agents' responses. Your vote is public.

Your personality:
{agent.persona}

Your voting criteria:
{agent.voting_criteria}

Arena history:
{feedback if feedback else "(No history yet)"}

Rules:
- You CANNOT vote for yourself
- Vote based on your criteria
- Valid choices: {valid_names_str}"""

    user_prompt = f"""Question: {question}

Responses:
{responses_text}

Vote for one agent by name. You must vote for one of: {valid_names_str}"""

    for attempt in range(max_retries):
        result = ollama.chat(
            model=agent.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format={
                "type": "object",
                "properties": {
                    "vote": {"type": "string"},
                    "reasoning": {"type": "string"}
                },
                "required": ["vote", "reasoning"]
            },
        )

        content = result["message"]["content"]
        vote_data = json.loads(content)
        voted_name = vote_data["vote"]

        if voted_name in valid_names:
            return Vote(
                voter_id=agent.personality_id,
                voter_name=agent.name,
                voted_for_id=name_to_id[voted_name],
                voted_for_name=voted_name,
                reasoning=vote_data.get("reasoning"),
            )

        # Invalid vote, retry with stricter prompt
        user_prompt = f"""Your previous vote "{voted_name}" was invalid. You cannot vote for yourself.

Vote again. You MUST choose one of: {valid_names_str}"""

    # All retries failed, pick randomly
    import random
    fallback_name = random.choice(valid_names)
    return Vote(
        voter_id=agent.personality_id,
        voter_name=agent.name,
        voted_for_id=name_to_id[fallback_name],
        voted_for_name=fallback_name,
        reasoning="(random fallback after invalid votes)",
    )