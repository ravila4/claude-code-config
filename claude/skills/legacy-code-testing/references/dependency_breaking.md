# Dependency Breaking Catalog

This reference provides comprehensive patterns for breaking dependencies in legacy Python code to enable testing.

---

## 1. Parameterize Constructor

**When to use:** You can modify the constructor and want to inject test doubles.

**Difficulty:** Easy

**Pattern:**

```python
# BEFORE - Hard-coded dependency
class ReportGenerator:
    def __init__(self):
        self.db = PostgresConnection()
        self.emailer = SMTPEmailer()
        self.logger = FileLogger('/var/log/app.log')

    def generate(self, report_id):
        data = self.db.query(f"SELECT * FROM reports WHERE id={report_id}")
        report = self._create_report(data)
        self.emailer.send(report)
        self.logger.info(f"Report {report_id} sent")

# AFTER - Dependencies injected with production defaults
class ReportGenerator:
    def __init__(self, db=None, emailer=None, logger=None):
        self.db = db or PostgresConnection()
        self.emailer = emailer or SMTPEmailer()
        self.logger = logger or FileLogger('/var/log/app.log')

    def generate(self, report_id):
        data = self.db.query(f"SELECT * FROM reports WHERE id={report_id}")
        report = self._create_report(data)
        self.emailer.send(report)
        self.logger.info(f"Report {report_id} sent")

# Test with mocks
def test_generate_sends_email():
    mock_db = Mock()
    mock_db.query.return_value = [{'id': 1, 'data': 'test'}]
    mock_emailer = Mock()
    mock_logger = Mock()

    generator = ReportGenerator(db=mock_db, emailer=mock_emailer, logger=mock_logger)
    generator.generate(1)

    mock_emailer.send.assert_called_once()
    mock_logger.info.assert_called_once()
```

**Key points:**
- Always provide production defaults (`db or PostgresConnection()`)
- Inject all external dependencies
- Production code unchanged (still works without arguments)
- Test code can inject mocks

---

## 2. Extract Interface (Protocol)

**When to use:** Need multiple implementations or want stronger type checking.

**Difficulty:** Medium

**Pattern:**

```python
from typing import Protocol

# Define protocol for required behavior
class DataSource(Protocol):
    def fetch(self, key: str) -> dict: ...
    def save(self, key: str, data: dict) -> None: ...

# Production implementation
class PostgresDataSource:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)

    def fetch(self, key: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM data WHERE key = %s", (key,))
        return cursor.fetchone()

    def save(self, key: str, data: dict) -> None:
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO data VALUES (%s, %s)", (key, json.dumps(data)))
        self.conn.commit()

# Test double implementation
class FakeDataSource:
    """In-memory test double"""
    def __init__(self):
        self.data = {}

    def fetch(self, key: str) -> dict:
        return self.data.get(key, {})

    def save(self, key: str, data: dict) -> None:
        self.data[key] = data

# Code depends on protocol, not concrete class
class Processor:
    def __init__(self, source: DataSource):
        self.source = source

    def process(self, key: str):
        data = self.source.fetch(key)
        transformed = self._transform(data)
        self.source.save(f"{key}_processed", transformed)
        return transformed

# Test uses fake implementation
def test_processor():
    fake_source = FakeDataSource()
    fake_source.data['test_key'] = {'value': 42}

    processor = Processor(source=fake_source)
    result = processor.process('test_key')

    assert result == expected
    assert 'test_key_processed' in fake_source.data
```

**Key points:**
- Protocol defines interface contract
- Multiple implementations possible
- Type checker enforces protocol compliance
- Test doubles are full implementations, not mocks

---

## 3. Subclass and Override (Extract and Override)

**When to use:** Can't modify constructor (framework instantiates it) or dealing with singletons/global state.

**Difficulty:** Medium

**Pattern:**

```python
# BEFORE - Global state/singleton makes testing hard
class DataCache:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RedisCache('production:6379')
        return cls._instance

class Processor:
    def process(self, data):
        cache = DataCache.get_instance()
        cached = cache.get(data.id)
        if cached:
            return cached
        result = self._expensive_operation(data)
        cache.set(data.id, result)
        return result

# AFTER - Extract method for override point
class Processor:
    def process(self, data):
        cache = self._get_cache()  # Extracted - override point
        cached = cache.get(data.id)
        if cached:
            return cached
        result = self._expensive_operation(data)
        cache.set(data.id, result)
        return result

    def _get_cache(self):
        """Override point for testing"""
        return DataCache.get_instance()

# Test by subclassing
class TestableProcessor(Processor):
    def __init__(self, test_cache):
        self.test_cache = test_cache

    def _get_cache(self):
        return self.test_cache

def test_processor_uses_cache():
    mock_cache = Mock()
    mock_cache.get.return_value = 'cached_result'

    processor = TestableProcessor(test_cache=mock_cache)
    result = processor.process(Mock(id='123'))

    assert result == 'cached_result'
    mock_cache.get.assert_called_once_with('123')
```

**Key points:**
- Extract method creates "seam" for testing
- Production code uses original logic
- Test code subclasses and overrides
- Minimal changes to production class

---

## 4. Sprout Method

**When to use:** Adding new functionality to legacy code; want to test new code without testing legacy.

**Difficulty:** Easy

**Pattern:**

```python
# BEFORE - Giant untestable method
class LegacyProcessor:
    def process_batch(self, records):
        # ... 200 lines of spaghetti code ...
        # New feature needed somewhere in here
        pass

# AFTER - Sprout new testable method
class LegacyProcessor:
    def process_batch(self, records):
        # ... 200 lines of spaghetti code (unchanged) ...

        # New, testable code sprouted as separate method
        validated_records = self._validate_new_format(records)

        # Continue with legacy code (unchanged)
        # ... more spaghetti ...

    def _validate_new_format(self, records):
        """New method - fully tested before integration"""
        return [r for r in records if self._is_valid_format(r)]

    def _is_valid_format(self, record):
        """Testable validation logic"""
        return 'required_field' in record and record['required_field'] is not None

# Tests written BEFORE integration
def test_validate_new_format_filters_invalid():
    processor = LegacyProcessor()
    records = [
        {'required_field': 'value'},
        {'required_field': None},
        {},
    ]

    result = processor._validate_new_format(records)

    assert len(result) == 1
    assert result[0]['required_field'] == 'value'
```

**Key points:**
- New code isolated from legacy
- Test new code independently
- Legacy code remains untouched
- Low risk - only calling new method

---

## 5. Sprout Class

**When to use:** New functionality is substantial; want complete separation from legacy.

**Difficulty:** Easy

**Pattern:**

```python
# BEFORE - Need to add complex validation to legacy processor
class LegacyDataProcessor:
    def process(self, data):
        # ... 300 lines of legacy code ...
        # Need to add complex validation here
        pass

# AFTER - Sprout new class
class DataValidator:
    """New class - fully tested independently"""
    def __init__(self, rules):
        self.rules = rules

    def validate(self, data):
        errors = []
        for rule in self.rules:
            if not rule.check(data):
                errors.append(rule.error_message)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

class LegacyDataProcessor:
    def process(self, data):
        # ... 300 lines of legacy code ...

        # Use new, tested class
        validator = DataValidator(rules=self._get_validation_rules())
        result = validator.validate(data)
        if not result.is_valid:
            raise ValidationError(result.errors)

        # Continue with legacy code
        pass

# Comprehensive tests for new class
def test_validator_accepts_valid_data():
    rules = [RequiredFieldRule('id'), TypeRule('value', int)]
    validator = DataValidator(rules)

    result = validator.validate({'id': 123, 'value': 456})

    assert result.is_valid == True

def test_validator_rejects_invalid_data():
    rules = [RequiredFieldRule('id')]
    validator = DataValidator(rules)

    result = validator.validate({'name': 'test'})

    assert result.is_valid == False
    assert 'id' in str(result.errors)
```

**Key points:**
- Complete separation from legacy
- New class is independently testable
- Clear responsibility boundary
- Can evolve new class without touching legacy

---

## 6. Wrap Method

**When to use:** Need to add logic before/after existing method; want to preserve old logic untouched.

**Difficulty:** Easy

**Pattern:**

```python
# BEFORE - Can't test new preprocessing mixed with old export logic
class DataExporter:
    def export(self, data):
        # Old, working (but untested) export logic
        file = open('export.csv', 'w')
        for row in data:
            file.write(','.join(row))
        file.close()

# AFTER - Wrap with new, testable preprocessing
class DataExporter:
    def export(self, data):
        """Public method - now wraps old and new logic"""
        sanitized_data = self._sanitize_data(data)  # New, testable
        self._export_original(sanitized_data)       # Old, preserved

    def _sanitize_data(self, data):
        """New method - fully tested"""
        return [
            [self._clean_field(field) for field in row]
            for row in data
        ]

    def _clean_field(self, field):
        """Remove null bytes, strip whitespace"""
        return str(field).replace('\x00', '').strip()

    def _export_original(self, data):
        """Original logic - unchanged, untested (for now)"""
        file = open('export.csv', 'w')
        for row in data:
            file.write(','.join(row))
        file.close()

# Test new logic in isolation
def test_sanitize_data_removes_null_bytes():
    exporter = DataExporter()
    dirty_data = [['value\x00with\x00nulls', '  spaces  ']]

    result = exporter._sanitize_data(dirty_data)

    assert result == [['valuewithnulls', 'spaces']]
```

**Key points:**
- Rename original method (append `_original`)
- Create new public method that wraps both
- Test new logic independently
- Old logic preserved exactly as-is

---

## Decision Matrix

| Your Constraint | Recommended Technique |
|-----------------|----------------------|
| Can change constructor | Parameterize Constructor |
| Can't change constructor | Extract and Override |
| Dealing with singleton/global | Extract and Override |
| Adding new feature | Sprout Method or Sprout Class |
| Wrapping existing behavior | Wrap Method |
| Need type safety | Extract Interface (Protocol) |
| Large new feature | Sprout Class |
| Small new behavior | Sprout Method |

---

## Common Mistakes

### Forgetting Production Defaults

**Bad:**
```python
def __init__(self, db):  # Breaks existing code!
    self.db = db
```

**Good:**
```python
def __init__(self, db=None):
    self.db = db or ProductionDB()  # Works for prod and test
```

### Over-Refactoring Before Testing

**Bad:** Rewrite everything, break all dependencies, then try to write tests.

**Good:** Break one dependency, write tests for that area, repeat.

### Using Sprout When Parameterize Would Work

**Consider:** Sprout is great for adding new features, but if you're refactoring existing logic, Parameterize Constructor is often simpler.

---

## Examples by Python Framework

### Django Views

```python
# Extract database queries
class OrderView:
    def __init__(self, order_repo=None):
        self.order_repo = order_repo or OrderRepository()

    def get(self, request, order_id):
        order = self.order_repo.get_by_id(order_id)
        return JsonResponse(order.to_dict())
```

### Flask Routes

```python
# Parameterize service layer
@app.route('/users/<user_id>')
def get_user(user_id, user_service=None):
    service = user_service or UserService()
    user = service.get_user(user_id)
    return jsonify(user)
```

### FastAPI

```python
# Use dependency injection built-in
from fastapi import Depends

def get_db():
    return Database()

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: Database = Depends(get_db)):
    return db.get_item(item_id)

# Test with override
from fastapi.testclient import TestClient

def get_test_db():
    return FakeDatabase()

app.dependency_overrides[get_db] = get_test_db
client = TestClient(app)
```

---

**Remember:** The goal is minimal, safe changes to enable testing. Don't try to perfect the design before you have tests - get tests in place first, then refactor incrementally under coverage.
