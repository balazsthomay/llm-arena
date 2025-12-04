# llm-arena



ollama pull gemma3:12b
ollama pull qwen3:8b
ollama pull mistral:7b
ollama pull phi4:14b
ollama pull llama3.2:latest

A few questions you can ask:

1. What makes a good leader?
2. Should we fear artificial intelligence?
3. Is mathematics discovered or invented?
4. What's the most important scientific breakthrough of the last century?
5. Can war ever be justified?
6. What should humanity prioritize in the next 50 years?
7. Is privacy dead?
8. What makes art valuable?
9. Should we abolish prisons?
10. Is social media making us lonelier?
11. What's the best way to raise children?
12. Can money buy happiness?
13. Should voting be mandatory?
14. What defines consciousness?
15. Is space exploration worth the cost?
16. Should animals have legal rights?
17. What's the ideal form of government?
18. Is free will an illusion?
19. What should schools teach that they currently don't?
20. Can algorithms be racist?
21. What's more important: freedom or security?
22. Should we genetically modify humans?
23. What makes a life meaningful?
24. Is nationalism good or bad?
25. Should billionaires exist?
26. What's the biggest threat to humanity?
27. Is meritocracy a myth?
28. Should euthanasia be legal?
29. What defines personal identity?
30. Will humans ever achieve world peace?


INIT: Load 5 starter personalities → Assign random models → Create Agents → Save state

                                         ↓

┌─────────────────────────── ROUND LOOP (x30) ───────────────────────────┐
│                                                                        │
│  1. RESPONSES                                                          │
│     You ask question → Each agent generates answer (sees feedback.md)  │
│                                                                        │
│  2. VOTING                                                             │
│     Each agent votes for one other (sees all responses except own)     │
│     Invalid vote → retry 2x → fallback to random                       │
│                                                                        │
│  3. TALLY                                                              │
│     Count votes → Update stats (drought++ if 0 votes)                  │
│     Append to feedback.md (keep last 5) → Save round log               │
│                                                                        │
│  4. ELIMINATION (every 3 rounds)                                       │
│     drought >= 3 → Remove agent → Meta-LLM generates replacement       │
│     (sees survivors + eliminated + feedback.md)                        │
│                                                                        │
│  Save state → Next round                                               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

                                         ↓

END: Show surviving agents, total votes, elimination history