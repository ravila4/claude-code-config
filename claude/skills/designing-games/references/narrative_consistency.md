# Narrative Consistency Checklist

Ensuring story, world, and character coherence in text-based games.

## State Persistence

### Object State

- [ ] Objects moved by player stay moved
- [ ] Objects changed by player stay changed (doors opened, switches flipped)
- [ ] Destroyed/consumed items don't reappear
- [ ] Container contents persist

**Test:** Take an item in Act 1, return to location in Act 3. Is it still gone?

### NPC Memory

- [ ] NPCs remember meeting the player
- [ ] NPCs remember player actions that affected them
- [ ] NPCs reference shared history in dialogue
- [ ] Relationship changes persist

**Test:** Betray an NPC, leave, return. Do they still trust you?

### World State

- [ ] Environmental changes persist (battles, disasters)
- [ ] Faction relationships reflect player actions
- [ ] News/rumors reflect recent events
- [ ] Time-sensitive events progress appropriately

**Test:** If you cause a war, does the world show it?

## Branching Coherence

### Path Consistency

- [ ] Information learned on one path doesn't appear on another without justification
- [ ] Character knowledge matches what they've experienced
- [ ] Skills/items only available if acquired
- [ ] Past choices are referenced when relevant

**Test:** Take Path A, note what protagonist knows. Start over, take Path B. Any impossible knowledge?

### Convergence Logic

When branches rejoin:
- [ ] Dialogue accounts for different paths to this point
- [ ] Character reactions appropriate to what the player did
- [ ] No "phantom" references to events that didn't happen
- [ ] Stakes/relationships reflect history

**Test:** Reach convergence point via different routes. Does it make sense both ways?

### Dead Ends

- [ ] Every ending is intentional
- [ ] Dead ends have closure (not just "Game Over")
- [ ] Players can recognize when they've reached an end
- [ ] Bad endings feel earned, not arbitrary

**Test:** Can a player accidentally get stuck without knowing why?

## Character Consistency

### Motivation Tracking

- [ ] Characters act according to established goals
- [ ] Motivation changes are shown, not assumed
- [ ] Betrayals have foreshadowing
- [ ] Allies don't become enemies without reason

**Test:** Can you explain why each character does what they do?

### Knowledge Boundaries

- [ ] Characters only know what they could know
- [ ] Secrets stay secret until revealed
- [ ] No "psychic" awareness of off-screen events
- [ ] Dramatic irony is intentional

**Test:** Does any character know something they shouldn't?

### Voice Consistency

- [ ] Each character has distinct speech patterns
- [ ] Speech patterns remain consistent
- [ ] Emotional register matches situation
- [ ] Cultural/background details are coherent

**Test:** Remove speaker tags. Can you identify who's talking?

## World Rules

### Systematic Consistency

- [ ] Magic/technology follows established rules
- [ ] Exceptions are explained or foreshadowed
- [ ] Power levels are consistent
- [ ] Limitations matter

**Test:** Could a reader predict what's possible from established rules?

### Geographic Consistency

- [ ] Distances make sense
- [ ] Travel time is appropriate
- [ ] Places are where they should be
- [ ] Climate/terrain is coherent

**Test:** Map the world. Does it work?

### Temporal Consistency

- [ ] Events happen in logical order
- [ ] Time passes consistently
- [ ] Flashbacks are clear
- [ ] No impossible timelines

**Test:** Create a timeline. Any contradictions?

## The "Because Plot" Test

For every major event, ask: "Why did this happen?"

**Good answers:**
- Character motivation (they wanted X)
- Logical consequence (Y caused Z)
- Established world rule (this always happens when...)

**Bad answer:**
- "Because the plot needed it to happen"

If you can only answer "because plot," the narrative needs work.

## Common Consistency Bugs

| Bug | Example | Fix |
|-----|---------|-----|
| **Resurrection** | Destroyed item reappears | Track destruction flags |
| **Amnesia** | NPC forgets player actions | Check relationship state |
| **Clairvoyance** | Character knows unrevealed info | Guard information flow |
| **Teleportation** | Location continuity break | Enforce spatial logic |
| **Personality flip** | Character acts against type | Review motivation chain |
| **Magic expansion** | System gains new powers arbitrarily | Establish limits early |

## Six-Pass Checklist (from Choice of Games)

When reviewing narrative:

1. **Structural pass:** Do all paths connect sensibly?
2. **Consistency pass:** Are there contradictions?
3. **Knowledge pass:** Does everyone know only what they should?
4. **Motivation pass:** Do all actions have reasons?
5. **Consequence pass:** Do choices lead to appropriate outcomes?
6. **Polish pass:** Does the prose support the story?
