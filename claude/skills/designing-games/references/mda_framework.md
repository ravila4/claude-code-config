# MDA Framework Reference

Mechanics-Dynamics-Aesthetics framework by Hunicke, LeBlanc, and Zubek.

## The Three Layers

### Mechanics (Rules)

The formal components: data structures, algorithms, rules that define interactions.

**In text-based games:**
- State variables (inventory, flags, stats)
- Transition rules (what choices lead where)
- Resource systems (health, currency, time)
- Randomization (dice rolls, chance events)

**Questions to ask:**
- What can the player do?
- What does the system track?
- What determines outcomes?

### Dynamics (Behavior)

What happens when mechanics meet player input. Emergent behavior, strategies, patterns.

**In text-based games:**
- Pacing (how fast events unfold)
- Tension (stakes, uncertainty)
- Discovery patterns (how players explore)
- Meta-strategies (how players optimize)

**Questions to ask:**
- What behaviors do the mechanics encourage?
- What patterns emerge in playthroughs?
- Where do players get stuck or rush?

### Aesthetics (Experience)

The emotional responses evoked. What the player *feels*.

**The Eight Aesthetics:**

| Aesthetic | Definition | Text Game Example |
|-----------|------------|-------------------|
| **Sensation** | Sense-pleasure | Rich prose, evocative descriptions |
| **Fantasy** | Make-believe | Role-playing a character unlike yourself |
| **Narrative** | Drama | Compelling story with meaningful stakes |
| **Challenge** | Mastery | Puzzles, difficult choices, skill tests |
| **Fellowship** | Social | Multiplayer, shared experience |
| **Discovery** | Exploration | Hidden content, secrets, world lore |
| **Expression** | Self-discovery | Character customization, moral choices |
| **Submission** | Relaxation | Low-stakes wandering, atmosphere |

## Applying MDA

### Design Direction (Designer → Player)

1. Choose target aesthetics first: "What should players *feel*?"
2. Design dynamics that produce those feelings
3. Implement mechanics that create those dynamics

**Example:**
- Target: **Challenge** + **Discovery**
- Dynamics: Branching paths with hidden areas, escalating difficulty
- Mechanics: Skill checks, locked areas requiring items, optional content flags

### Analysis Direction (Player → Designer)

When diagnosing problems:

1. Identify the aesthetic failure: "It feels boring/unfair/confusing"
2. Trace to dynamics: "What behavior is causing this?"
3. Trace to mechanics: "What rule creates that behavior?"

**Example:**
- Problem: "Choices feel meaningless" (Aesthetic: low Expression/Challenge)
- Dynamics: All paths converge to same outcome
- Mechanics: Branching structure reconverges too quickly

### Common MDA Misalignments

| Symptom | Likely Cause | Fix Direction |
|---------|--------------|---------------|
| "It's boring" | Missing Challenge/Discovery | Add stakes, secrets, or skill tests |
| "Choices don't matter" | Dynamics converge regardless of input | Increase branch divergence |
| "Too hard" | Challenge without Sensation/Narrative to motivate | Add beauty or story stakes |
| "Confusing" | Mechanics opaque, dynamics unpredictable | Clarify rules, add feedback |
| "No reason to explore" | Missing Discovery incentives | Add hidden content, rewards |

## MDA for Text-Based Genres

### Interactive Fiction (Choice-Based)

Primary aesthetics: **Narrative**, **Expression**, **Discovery**

Mechanics to emphasize:
- Meaningful branching (choices have consequences)
- State tracking (world remembers decisions)
- Pacing control (player agency over tempo)

### Parser IF (Command-Based)

Primary aesthetics: **Challenge**, **Discovery**, **Fantasy**

Mechanics to emphasize:
- Puzzle design (logical, fair)
- World simulation (consistent object interactions)
- Exploration rewards (secrets worth finding)

### Text RPG

Primary aesthetics: **Challenge**, **Expression**, **Fantasy**

Mechanics to emphasize:
- Character progression (stats, skills)
- Combat/encounter balance
- Build diversity (multiple viable approaches)

## Using MDA in Review

When reviewing a game, analyze each finding through MDA:

```
Finding: "The final boss is too easy"

MDA Analysis:
- Mechanic: Boss has 100 HP, player does 50 damage/turn
- Dynamic: Fight ends in 2 turns with no tension
- Aesthetic: Missing Challenge; climax feels anticlimactic

Suggested directions:
- Increase boss HP (mechanic change)
- Add boss phases/abilities (mechanic change)
- Add narrative stakes that make the fight feel important (aesthetic boost)
```
