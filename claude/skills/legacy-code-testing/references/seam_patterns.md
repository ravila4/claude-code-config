# Seam Patterns in Python

A **seam** is a place where you can alter behavior for testing without editing the code at that point. Understanding seams is key to testing legacy code.

---

## Contents

- [What is a Seam?](#what-is-a-seam)
- [Types of Seams in Python](#types-of-seams-in-python)
- [Finding Seams](#finding-seams)
- [Creating Seams](#creating-seams)
- [Seam Quality Checklist](#seam-quality-checklist)
- [Common Seam Mistakes](#common-seam-mistakes)
- [Seam Selection Guide](#seam-selection-guide)
- [Quick Reference: Creating Object Seams](#quick-reference-creating-object-seams)

## What is a Seam?

Every seam has two parts:
1. **The seam** - A place where behavior can vary
2. **The enabling point** - Where you control which behavior is used

---

## Types of Seams in Python

### 1. Object Seam (Most Common)

**The seam:** Method calls on objects
**Enabling point:** Which object you pass in

**Example:**

```python
# The seam: self.db.query()
class UserService:
    def __init__(self, db=None):
        self.db = db or ProductionDB()  # Enabling point

    def get_user(self, user_id):
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# Production: Uses ProductionDB
service = UserService()

# Test: Uses MockDB
service = UserService(db=MockDB())
```

**When to use:**
- Most common pattern
- Works for class dependencies
- Preferred for new code

### 2. Link Seam (Import/Module Level)

**The seam:** Imported modules or functions
**Enabling point:** `monkeypatch` or `mock.patch`

**Example:**

```python
# Code under test
import requests

def fetch_data(url):
    response = requests.get(url)  # Seam: requests.get
    return response.json()

# Test - enabling point: monkeypatch
def test_fetch_data(monkeypatch):
    mock_get = Mock(return_value=Mock(json=lambda: {'data': 'test'}))
    monkeypatch.setattr('requests.get', mock_get)  # Enabling point

    result = fetch_data('http://example.com')

    assert result['data'] == 'test'
```

**When to use:**
- Can't modify the code to inject dependencies
- Dealing with third-party libraries
- Module-level functions

### 3. Preprocessing Seam (Less Common in Python)

**The seam:** Code executed before main code
**Enabling point:** Environment setup, fixtures

**Example:**

```python
# Code reads environment variable
import os

def get_api_key():
    return os.environ.get('API_KEY')  # Seam: environment

# Test - enabling point: fixture sets environment
@pytest.fixture
def test_env(monkeypatch):
    monkeypatch.setenv('API_KEY', 'test-key-123')  # Enabling point

def test_get_api_key(test_env):
    assert get_api_key() == 'test-key-123'
```

---

## Finding Seams

### Look for Dependencies

Ask these questions about each method:
1. Does it create objects internally? → **Object seam candidate**
2. Does it call global functions/modules? → **Link seam candidate**
3. Does it read global state/environment? → **Preprocessing seam candidate**

### Example Analysis

```python
class OrderProcessor:
    def process_order(self, order_id):
        # Seam 1: Database (object seam)
        db = PostgresDB('production')
        order = db.get_order(order_id)

        # Seam 2: Email service (object seam)
        emailer = SMTPEmailer()
        emailer.send_confirmation(order.customer_email)

        # Seam 3: Payment gateway (link seam)
        response = stripe.charge(order.total)

        # Seam 4: Logging (preprocessing seam)
        logger.info(f"Processed order {order_id}")
```

**Opportunities:**
- Inject `db` and `emailer` → Object seams
- Patch `stripe.charge` → Link seam
- Configure `logger` in fixture → Preprocessing seam

---

## Creating Seams

### Pattern 1: Extract Dependency Creation

**Before:**
```python
class Processor:
    def process(self):
        db = create_database_connection()  # Hard-coded
        return db.query(...)
```

**After (Object Seam):**
```python
class Processor:
    def __init__(self, db=None):
        self.db = db or create_database_connection()

    def process(self):
        return self.db.query(...)
```

### Pattern 2: Extract Method to Create Override Point

**Before:**
```python
class Processor:
    def process(self):
        cache = GlobalCache.get_instance()  # Singleton, can't inject
        return cache.get('key')
```

**After (Extract and Override):**
```python
class Processor:
    def process(self):
        cache = self._get_cache()  # Extracted - seam!
        return cache.get('key')

    def _get_cache(self):
        return GlobalCache.get_instance()

# Test subclass overrides
class TestableProcessor(Processor):
    def __init__(self, test_cache):
        self.test_cache = test_cache

    def _get_cache(self):
        return self.test_cache  # Enabling point
```

### Pattern 3: Introduce Seam Without Changing Callers

**Before:**
```python
def send_email(to, subject, body):
    smtp = smtplib.SMTP('mail.example.com')  # Hard-coded
    smtp.send(to, subject, body)
```

**After (Default Parameter):**
```python
def send_email(to, subject, body, smtp_client=None):
    smtp = smtp_client or smtplib.SMTP('mail.example.com')  # Seam
    smtp.send(to, subject, body)

# Production calls unchanged
send_email('user@example.com', 'Hello', 'World')

# Tests inject mock
send_email('user@example.com', 'Hello', 'World', smtp_client=MockSMTP())
```

---

## Seam Quality Checklist

Good seams are:
- ✅ **Minimal** - Small, focused change to enable testing
- ✅ **Safe** - Don't change production behavior
- ✅ **Clear** - Obvious what behavior is being replaced
- ✅ **Accessible** - Enabling point is reachable from tests

Bad seams:
- ❌ Require extensive refactoring
- ❌ Change production logic
- ❌ Obscure what's being tested
- ❌ Nested deep in private methods

---

## Common Seam Mistakes

### Mistake 1: Seam Too Deep

**Problem:**
```python
class Processor:
    def process(self):
        return self._step1()

    def _step1(self):
        return self._step2()

    def _step2(self):
        db = PostgresDB()  # Seam buried 3 levels deep!
        return db.query(...)
```

**Solution:** Extract to constructor or pass as parameter:
```python
class Processor:
    def __init__(self, db=None):
        self.db = db or PostgresDB()  # Seam at construction

    def process(self):
        return self._step1()

    def _step1(self):
        return self._step2()

    def _step2(self):
        return self.db.query(...)
```

### Mistake 2: Multiple Seams in One Place

**Problem:**
```python
def process(self, data):
    db = PostgresDB()
    cache = RedisCache()
    logger = FileLogger()
    emailer = SMTPEmailer()
    # Too many seams!
```

**Solution:** Group into single dependency or use facade:
```python
class ServiceDependencies:
    def __init__(self, db=None, cache=None, logger=None, emailer=None):
        self.db = db or PostgresDB()
        self.cache = cache or RedisCache()
        self.logger = logger or FileLogger()
        self.emailer = emailer or SMTPEmailer()

def __init__(self, deps=None):
    self.deps = deps or ServiceDependencies()
```

---

## Seam Selection Guide

| Situation | Seam Type | Difficulty |
|-----------|-----------|------------|
| Class creates dependencies | Object Seam | Easy |
| Using third-party library | Link Seam | Easy |
| Singleton/static method | Extract & Override | Medium |
| Can't modify constructor | Extract & Override | Medium |
| Environment/config dependent | Preprocessing Seam | Easy |
| Legacy code, no changes allowed | Link Seam | Easy |

---

## Quick Reference: Creating Object Seams

1. **Identify the dependency** - What external object/service is created?
2. **Add constructor parameter** - `def __init__(self, dep=None):`
3. **Provide production default** - `self.dep = dep or ProductionDep()`
4. **Use in method** - Replace inline creation with `self.dep`
5. **Test by injecting** - `obj = MyClass(dep=MockDep())`

**Remember:** Seams enable testing without changing behavior. Start with simple object seams, use link seams when you can't modify the code.
