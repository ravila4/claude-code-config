---
name: legacy-code-testing
description: Use when dealing with hard-to-test legacy code that has tight coupling, hidden dependencies, or singletons. Provides seam identification, dependency breaking patterns, and characterization testing strategies.
---

# Legacy Code Testing

## Overview

Transform untested, tightly-coupled legacy Python code into testable components using proven techniques from Michael Feathers' "Working Effectively with Legacy Code". This skill provides practical patterns for adding tests to code that wasn't designed with testing in mind.

## The Legacy Code Dilemma

> "To change code safely, we need tests. To add tests, we often need to change code. But changing code without tests is risky."
> — Michael Feathers

**This skill solves that dilemma** by teaching you to find "seams" (places where you can change behavior without editing code) and apply minimal-risk dependency breaking techniques.

## When to Use This Skill

Use when facing:
- **Untested production code** that needs modification
- **Tight coupling** - Classes instantiate their own dependencies
- **Hidden dependencies** - Global state, singletons, static methods
- **Hard-coded infrastructure** - Database connections, file I/O, network calls baked in
- **God classes** - 500+ line classes doing everything
- **Spaghetti code** - No clear separation of concerns

**Don't use for:**
- New code (use `test-driven-development` skill instead)
- Already well-tested code (use `testing-anti-patterns` for improvements)

## The Legacy Code Change Algorithm

Follow this sequence when changing legacy code:

1. **Identify change points** - Where does the code need to change?
2. **Find test points** - Where can you write tests? (Often different from change points!)
3. **Break dependencies** - Make test points accessible
4. **Write tests** - Start with characterization tests
5. **Make changes** - Now you have a safety net
6. **Refactor** - Improve the code under test coverage

## Core Techniques

### 1. Seam Identification

A **seam** is a place where you can alter behavior without editing the code. Python has two main types:

#### Object Seam (Most Common)

Use dependency injection to make dependencies replaceable.

**Before - Hard to test:**
```python
class DataProcessor:
    def process(self, data_id):
        db = PostgresDB('prod_connection')  # Hard-coded!
        raw_data = db.fetch(data_id)
        return self._transform(raw_data)
```

**After - Testable:**
```python
class DataProcessor:
    def __init__(self, db=None):
        self.db = db or PostgresDB('prod_connection')

    def process(self, data_id):
        raw_data = self.db.fetch(data_id)
        return self._transform(raw_data)

# Test with mock
def test_process_transforms_data():
    mock_db = Mock()
    mock_db.fetch.return_value = {'value': 10}
    processor = DataProcessor(db=mock_db)

    result = processor.process(123)

    assert result == expected_output
```

#### Link Seam (Import/Module Level)

Replace imports or module-level functions during testing.

**Code using external dependency:**
```python
import requests

def fetch_user_data(user_id):
    response = requests.get(f'https://api.example.com/users/{user_id}')
    return response.json()
```

**Test using link seam:**
```python
def test_fetch_user_data(monkeypatch):
    mock_get = Mock(return_value=Mock(json=lambda: {'id': 1, 'name': 'Test'}))
    monkeypatch.setattr('requests.get', mock_get)

    result = fetch_user_data(1)

    assert result['name'] == 'Test'
```

### 2. Characterization Tests

**Purpose:** Preserve existing behavior when you don't fully understand the code yet.

**Strategy:**
1. Run the code with various inputs
2. Observe the outputs
3. Write tests that document what it **does** (not what it **should** do)
4. Now you can refactor safely - tests will catch behavioral changes

**Example:**
```python
# Legacy function - unclear logic
def calculate_discount(price, customer_type, order_count):
    # ... 50 lines of complex logic ...
    return final_price

# Characterization test - captures observed behavior
@pytest.mark.parametrize("price,customer_type,order_count,expected", [
    (100, 'regular', 5, 95.0),      # Observed from production
    (100, 'premium', 5, 85.0),      # Observed from production
    (100, 'regular', 15, 90.0),     # Observed from production
    (50, 'premium', 1, 47.5),       # Edge case observed
])
def test_calculate_discount_characterization(price, customer_type, order_count, expected):
    """
    Characterization test - captures current behavior before refactoring.
    These values were observed from the legacy system on 2025-01-15.

    TODO: Review if behavior is correct, then refactor with confidence.
    """
    result = calculate_discount(price, customer_type, order_count)
    assert result == expected
```

**When to use:**
- Code behavior is unclear
- No documentation exists
- Too risky to change without tests
- Preparing for refactoring

### 3. Dependency Breaking Catalog

Choose the right technique based on your constraints. See `references/dependency_breaking.md` for detailed patterns.

#### Quick Decision Guide

| Situation | Technique | Difficulty |
|-----------|-----------|------------|
| Can modify constructor | Parameterize Constructor | Easy |
| Need multiple implementations | Extract Interface (Protocol) | Medium |
| Can't change constructor | Subclass and Override | Medium |
| Adding new feature to legacy | Sprout Method/Class | Easy |
| Wrapping legacy with new logic | Wrap Method | Easy |
| Singleton/Global state | Extract and Override | Medium |

## Workflow

### Step 1: Assess the Code

Ask these questions:
- What needs to change?
- Where are the dependencies?
- Can I test this code in its current state?
- What seams exist?

### Step 2: Write Characterization Tests

Before breaking dependencies, capture current behavior:

```python
# Run code with various inputs, observe outputs
# Document findings as tests
@pytest.mark.characterization
def test_current_behavior():
    """Documents what code currently does"""
    result = legacy_function(input_1)
    assert result == observed_output_1  # From running the code
```

### Step 3: Break Dependencies

Apply minimal changes to enable testing:

```python
# Before: Hard-coded dependency
class Processor:
    def __init__(self):
        self.db = ProductionDB()  # Can't test!

# After: Dependency injection (minimal change)
class Processor:
    def __init__(self, db=None):
        self.db = db or ProductionDB()  # Production default, testable
```

### Step 4: Write Tests for Changes

Now you can test the specific behavior you're adding:

```python
def test_new_validation_logic():
    mock_db = Mock()
    processor = Processor(db=mock_db)

    # Test the new feature you're adding
    assert processor.validate_new_format(data) == True
```

### Step 5: Make Changes Safely

With tests in place:
1. Make your changes
2. Run characterization tests (should still pass - behavior preserved)
3. Run new tests (should pass - new feature works)
4. Refactor under test coverage

## Integration with Other Testing Skills

This skill complements the testing ecosystem:

**test-driven-development:**
- Use TDD for **new code** within legacy systems
- Use sprout method/class to add testable code alongside legacy

**testing-anti-patterns:**
- Avoid over-mocking when breaking dependencies
- Don't add test-only methods to production classes
- Test real behavior, not mocks

**legacy-code-testing (this skill):**
- Use for **existing untested code**
- Provides techniques TDD doesn't cover (characterization, seams)
- Bridges the gap between "no tests" and "comprehensive tests"

## Common Pitfalls

### Changing Too Much at Once

**Problem:** Breaking all dependencies before writing any tests.

**Solution:** Break one dependency, write tests, repeat. Small steps.

### Not Writing Characterization Tests First

**Problem:** Refactoring without knowing current behavior leads to silent bugs.

**Solution:** Always capture behavior first with characterization tests.

### Over-Engineering the Refactoring

**Problem:** Trying to perfect the design before having test coverage.

**Solution:** Get tests in place first, refactor incrementally under coverage.

### Ignoring Production Defaults

**Problem:** Dependency injection breaks production code if no default provided.

**Solution:** Always provide production defaults in constructors:
```python
def __init__(self, db=None):
    self.db = db or ProductionDB()  # Default for production
```

## Resources

This skill includes detailed reference material:

### references/

- `seam_patterns.md` - Comprehensive guide to identifying and using seams
- `dependency_breaking.md` - Full catalog of dependency breaking techniques with Python examples
- `characterization_testing.md` - Strategies for capturing legacy behavior
- `sprout_and_wrap.md` - Techniques for adding new code alongside legacy

See the [references directory](references/) for comprehensive documentation.

## Quick Reference Card

**When you see this → Use this technique:**

- Hard-coded database/API → Parameterize Constructor
- Singleton pattern → Extract and Override
- Giant method needing change → Sprout Method
- Need to preserve old logic → Wrap Method
- Complex class, unclear behavior → Characterization Tests
- Import-based coupling → Link Seam (monkeypatch)
- Multiple implementations needed → Extract Interface (Protocol)

**Remember:** The goal isn't perfect code. The goal is **safe change**. Get tests in place, then improve incrementally.
