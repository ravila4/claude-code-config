---
name: testing-anti-patterns
description: Guidance for writing and modifying tests, implementing mocks, or adding methods to production code. Prevents testing mock behavior, polluting production code with test-only methods, and mocking without understanding dependencies.
---

# Testing Anti-Patterns

## Overview

Recognize and avoid common testing mistakes that create fragile tests, pollute production code, and provide false confidence.

**Core Principle:** "Test what the code does, not what the mocks do."

## When to Use

Apply this skill when:
- Writing new tests
- Modifying existing tests
- Implementing mocks or test doubles
- Adding methods to production classes
- Reviewing test code
- Debugging failing tests

## The Three Iron Laws

### 1. Never Test Mock Behavior
Test real component functionality, not that mocks exist.

### 2. Never Add Test-Only Methods to Production Classes
Keep production code clean of testing concerns.

### 3. Never Mock Without Understanding Dependencies
Comprehend side effects before mocking them away.

## Anti-Patterns and Solutions

### Anti-Pattern 1: Testing Mock Behavior

**Problem:**
Verifying that mocks exist rather than validating actual component functionality.

**Example (Bad):**
```python
def test_user_service():
    mock_db = Mock()
    service = UserService(db=mock_db)

    result = service.get_user(123)

    # Testing that mock was called, not what service does!
    mock_db.fetch.assert_called_once_with(123)
```

**Solution:**
Test real component behavior, not mock presence.

**Example (Good):**
```python
def test_user_service():
    mock_db = Mock()
    mock_db.fetch.return_value = {'id': 123, 'name': 'Alice'}
    service = UserService(db=mock_db)

    result = service.get_user(123)

    # Testing what service actually returns
    assert result['name'] == 'Alice'
    assert result['id'] == 123
```

**Gate Function:**
Before asserting on any mock element, ask:
- "Am I testing real component behavior or just mock existence?"
- "What does this assertion tell me about production behavior?"

### Anti-Pattern 2: Test-Only Methods in Production

**Problem:**
Production classes polluted with methods exclusively used during testing.

**Example (Bad):**
```python
class UserCache:
    def __init__(self):
        self._cache = {}

    def get(self, user_id):
        return self._cache.get(user_id)

    def set(self, user_id, user):
        self._cache[user_id] = user

    # Test-only method polluting production class!
    def clear_for_testing(self):
        """Only used in tests"""
        self._cache.clear()
```

**Solution:**
Move cleanup logic to test utilities separate from production code.

**Example (Good):**
```python
# Production code (clean)
class UserCache:
    def __init__(self):
        self._cache = {}

    def get(self, user_id):
        return self._cache.get(user_id)

    def set(self, user_id, user):
        self._cache[user_id] = user

# Test utilities (separate)
@pytest.fixture
def clean_cache():
    cache = UserCache()
    yield cache
    # Cleanup via fixture, not production method

# Or use dependency injection
def test_cache():
    cache = UserCache()  # Fresh instance per test
    cache.set(1, {'name': 'Alice'})
    assert cache.get(1)['name'] == 'Alice'
```

**Gate Function:**
Before adding methods to production classes, ask:
- "Is this only used by tests?"
- "Does this class own this resource's lifecycle?"
- "Could this be used accidentally in production?"

### Anti-Pattern 3: Mocking Without Understanding

**Problem:**
Mocking methods without comprehending their side effects, breaking test logic when those effects are required.

**Example (Bad):**
```python
def test_data_processor():
    mock_db = Mock()
    # Mocking save() without realizing it updates state!
    mock_db.save.return_value = None

    processor = DataProcessor(db=mock_db)
    processor.process_and_save(data)

    # This fails because save() side effect was needed
    result = processor.get_last_saved()
    assert result == data  # FAIL: save() was mocked away
```

**Solution:**
Understand dependency chains completely; mock at lower levels that preserve necessary behavior.

**Example (Good):**
```python
def test_data_processor():
    # Use real object or mock at lower level
    db = InMemoryDB()  # Test double that preserves behavior

    processor = DataProcessor(db=db)
    processor.process_and_save(data)

    # Now side effects are preserved
    result = processor.get_last_saved()
    assert result == data  # PASS
```

**Gate Function:**
Before mocking, ask:
- "What side effects does this method have?"
- "Does my test depend on those side effects?"
- "Am I mocking at the right abstraction level?"
- "Could I use a test double instead of a mock?"

### Anti-Pattern 4: Incomplete Mocks

**Problem:**
Creating partial mock responses missing fields that downstream code consumes, causing silent failures.

**Example (Bad):**
```python
def test_user_formatter():
    mock_api = Mock()
    # Incomplete mock - missing 'email' field
    mock_api.get_user.return_value = {'name': 'Alice'}

    formatter = UserFormatter(api=mock_api)
    result = formatter.format_user(123)

    # Fails downstream when email is accessed
    assert result  # KeyError: 'email'
```

**Solution:**
Mirror complete real API structures, including all documented fields.

**Example (Good):**
```python
def test_user_formatter():
    mock_api = Mock()
    # Complete mock matching real API response
    mock_api.get_user.return_value = {
        'id': 123,
        'name': 'Alice',
        'email': 'alice@example.com',
        'created_at': '2025-01-01',
        'roles': ['user']
    }

    formatter = UserFormatter(api=mock_api)
    result = formatter.format_user(123)

    assert 'Alice' in result
    assert 'alice@example.com' in result
```

**Gate Function:**
Before creating mocks, ask:
- "What does the actual API response look like?"
- "What fields might downstream code consume?"
- "Have I examined real response samples?"

### Anti-Pattern 5: Integration Tests as Afterthought

**Problem:**
Testing treated as optional follow-up rather than integrated into implementation.

**Example (Bad):**
```python
# Write implementation first
def process_users(db, logger):
    users = db.fetch_all()
    for user in users:
        if user.active:
            logger.info(f"Processing {user.name}")
            db.update(user.id, {'processed': True})

# Then try to test it (awkward, requires complex mocking)
def test_process_users():
    mock_db = Mock()
    mock_logger = Mock()
    # Complex setup because we didn't think about testability
    mock_db.fetch_all.return_value = [...]
    # ... lots of mock setup ...
```

**Solution:**
Apply TDD methodology—write tests first, implement second.

**Example (Good):**
```python
# Write test first (defines interface)
def test_process_active_users():
    db = InMemoryDB()
    db.add_user(User(id=1, name='Alice', active=True))
    db.add_user(User(id=2, name='Bob', active=False))

    process_users(db)

    assert db.get_user(1).processed == True
    assert db.get_user(2).processed == False

# Then implement (naturally testable)
def process_users(db):
    for user in db.fetch_active_users():
        db.mark_processed(user.id)
```

**Gate Function:**
Before implementing, ask:
- "Have I written the test first?"
- "Is my implementation naturally testable?"

## TDD Connection

Test-driven development prevents these anti-patterns by:
- Forcing you to write failing tests against real code before mocking
- Ensuring tests validate genuine behavior, not mock existence
- Making testability a first-class design concern
- Revealing over-mocking early (if mocks dominate, design needs work)

**Use with test-driven-development skill for maximum effectiveness.**

## Red Flags

Watch for these warning signs:

### Mock-Focused Tests
- Assertions checking for mock test IDs
- More mock setup than actual test logic
- Tests passing even when production code is broken

### Production Pollution
- Methods appearing only in test files
- Methods with names like `clear_for_testing()`, `reset()`, `_test_helper()`
- Comments like "Only used in tests"

### Mock Overuse
- Mock setup exceeding 50% of test code
- Tests failing when mocks are removed
- Inability to explain why mocking is necessary
- Mocking "just to be safe"
- Every dependency mocked

### Design Smells
- Can't test without extensive mocking
- Tests break when refactoring (coupled to implementation details)
- Tests require knowledge of internal state

## Quick Reference

**Before writing a test:**
- [ ] Am I writing the test first? (TDD)
- [ ] What behavior am I testing?
- [ ] Do I need mocks, or can I use real objects?

**Before adding a mock:**
- [ ] Do I understand this dependency's side effects?
- [ ] Is this the right abstraction level to mock?
- [ ] Have I included all fields in mock responses?

**Before adding production methods:**
- [ ] Is this only used by tests?
- [ ] Could this be a test utility instead?

**When reviewing tests:**
- [ ] Are assertions about behavior, not mock calls?
- [ ] Would this test catch real bugs?
- [ ] Is the test setup simpler than the code being tested?

## Integration with Other Skills

**Works with:**
- test-driven-development (prevents anti-patterns through workflow)
- receiving-code-review (evaluate test quality in reviews)

**Complements:**
- Test engineering (comprehensive suite design)
- Legacy code refactoring (identifying test smells)
- Code review processes
