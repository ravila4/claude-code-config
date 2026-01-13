# Game Balance Principles

Frameworks and techniques for tuning difficulty, economy, and progression.

## The Sid Meier Method

**Double or halve, don't increment.**

When tuning values:
- Wrong: "Damage feels low, let's try 12 instead of 10"
- Right: "Damage feels low, let's try 20. Too high? Try 15."

Large changes reveal the *direction* of the problem. Small changes waste iterations.

## Power Curves

### Linear (Y = aX + b)

- Constant relationship between input and output
- Feels like steady progression
- Good for: basic stats, simple scaling

**Example:** Damage = Level × 5 + 10

### Quadratic (Y = aX² + bX + c)

- Small gains early, large gains late
- Creates "power spike" feeling
- Good for: making high-level content feel distinct

**Example:** XP required = Level² × 100

### Logarithmic (Y = a × log(X) + b)

- Large gains early, diminishing returns late
- Prevents stat inflation
- Good for: capping runaway systems

**Example:** Crit chance = 10 × log(Luck) (caps naturally)

## Economy Design

### Sources and Sinks

Every resource needs:
- **Sources**: Where it comes from (rewards, generation)
- **Sinks**: Where it goes (costs, decay, consumption)

**Balance rule:** Sources ≤ Sinks over time, or economy inflates.

### Faucets and Drains

More nuanced model:
- **Faucets**: Controllable sources (quest rewards, shops)
- **Drains**: Controllable sinks (upgrades, consumables)
- **Leaks**: Uncontrollable sources (grinding, exploits)
- **Cracks**: Uncontrollable sinks (death penalties, theft)

**Design goal:** Faucets and drains should be primary. Minimize leaks and cracks.

### Economy Red Flags

| Signal | Problem | Fix |
|--------|---------|-----|
| Player hoarding | Sinks not attractive | Add desirable purchases |
| Always broke | Sources too tight | Increase rewards or reduce costs |
| Infinite accumulation | No sinks | Add meaningful spending |
| Currency irrelevant | Too abundant | Reduce sources or add sinks |

## Difficulty Curve Design

### The Ideal Curve

```
Difficulty
    │      ╭─────╮
    │    ╱        ╲   ← Climax
    │  ╱            ╲
    │╱                ╲
    └──────────────────→ Time
      Tutorial    Mid    End
```

- Start easy (onboarding)
- Ramp steadily (learning)
- Peak at climax (challenge)
- Optional: drop for denouement

### Difficulty Components

**Mechanical difficulty:** How hard is execution?
- Input timing, resource management, optimization

**Strategic difficulty:** How hard is planning?
- Information gathering, decision-making, prediction

**Knowledge difficulty:** What must the player know?
- Rules understanding, system mastery, pattern recognition

Balance all three. Pure mechanical difficulty frustrates. Pure knowledge difficulty feels unfair.

## Stat Design

### The Useful Stat Test

Every stat should pass:
1. **Is it set?** Something must modify this stat.
2. **Is it checked?** Something must read and use this stat.
3. **Does it matter?** The check must have meaningful consequences.

**Red flags:**
- Stat set but never checked → remove it
- Stat checked but never set → stuck at default
- Stat changes don't affect gameplay → false complexity

### Avoiding Dominant Strategies

A dominant strategy is one that's always best, making other options irrelevant.

**Detection:**
- One build/path dramatically outperforms others
- Players discover "the right answer" and stop experimenting
- Community consensus emerges quickly

**Prevention:**
- Rock-paper-scissors relationships (A beats B beats C beats A)
- Situational strengths (good in combat, bad in stealth)
- Opportunity costs (can't have everything)

### Balance Formulas

Keep formulas simple. Every input makes tuning harder.

**Good:** Damage = Strength × WeaponBase

**Bad:** Damage = (Strength × 0.7 + Dexterity × 0.3) × WeaponBase × (1 + CritChance × CritMultiplier) × ElementalModifier × ...

If you can't explain it to a player, it's too complex.

## Testing Balance

### The Extremes Test

Simulate extreme players:
- **Optimizer:** Min-maxes everything. Does balance break?
- **Explorer:** Ignores optimization. Is the game still playable?
- **Casual:** Makes random choices. Are there death spirals?

### The Path Test

For branching games:
- Play the "easiest" path (highest rewards, lowest risk)
- Play the "hardest" path (lowest rewards, highest risk)
- Is the difficulty difference appropriate?

### Metrics to Track

If logging is available:
- Completion rates by path
- Resource totals at checkpoints
- Choice distributions
- Retry rates at challenges
