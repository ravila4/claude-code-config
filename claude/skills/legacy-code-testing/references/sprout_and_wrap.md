# Sprout and Wrap Techniques

When you need to add new functionality to legacy code but can't test the existing code, use **Sprout** or **Wrap** techniques to add testable code alongside untestable legacy.

---

## Sprout Method

**When to use:** Adding small new functionality to a legacy method.

**Strategy:** Extract new logic into a separate method that can be tested independently.

### Basic Pattern

```python
# BEFORE - Can't test new validation mixed with legacy
class LegacyProcessor:
    def process_batch(self, records):
        # ... 200 lines of untestable spaghetti ...
        # Need to add validation here
        # ... more spaghetti ...
        pass

# AFTER - Sprout testable validation method
class LegacyProcessor:
    def process_batch(self, records):
        # ... 200 lines of legacy (unchanged) ...

        # Call new, tested method
        valid_records = self._validate_records(records)

        # ... continue with legacy ...

    def _validate_records(self, records):
        """
        New method - fully tested BEFORE integration.
        Validates record format and required fields.
        """
        return [r for r in records if self._is_valid(r)]

    def _is_valid(self, record):
        """Testable validation logic"""
        required_fields = ['id', 'type', 'timestamp']
        return all(field in record for field in required_fields)

# Write tests FIRST, then integrate
def test_validate_records_filters_invalid():
    processor = LegacyProcessor()
    records = [
        {'id': 1, 'type': 'A', 'timestamp': '2025-01-20'},
        {'id': 2, 'type': 'B'},  # Missing timestamp
        {},                       # Missing everything
        {'id': 3, 'type': 'C', 'timestamp': '2025-01-20'},
    ]

    result = processor._validate_records(records)

    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[1]['id'] == 3
```

### Advantages
- ✅ New code is fully testable
- ✅ Legacy code remains untouched (low risk)
- ✅ Can use TDD for new method
- ✅ Clear separation between old and new

### Disadvantages
- ❌ Doesn't improve legacy code testability
- ❌ New method may need access to private state
- ❌ Can lead to method proliferation

---

## Sprout Class

**When to use:** New functionality is substantial enough to warrant its own class.

**Strategy:** Create a new, well-tested class and use it from legacy code.

### Basic Pattern

```python
# BEFORE - Need complex validation in legacy processor
class LegacyDataProcessor:
    def process(self, data):
        # ... 300 lines of legacy processing ...
        # Need to add complex multi-rule validation
        pass

# AFTER - Sprout new validator class
class DataValidator:
    """
    New class - designed for testability from the start.
    Handles all validation logic independently.
    """
    def __init__(self, rules):
        self.rules = rules

    def validate(self, data):
        errors = []
        for rule in self.rules:
            if not rule.applies_to(data):
                continue
            if not rule.check(data):
                errors.append(rule.error_message)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            data=data
        )

class LegacyDataProcessor:
    def process(self, data):
        # ... 300 lines of legacy (unchanged) ...

        # Use new, well-tested class
        validator = DataValidator(rules=self._get_validation_rules())
        result = validator.validate(data)

        if not result.is_valid:
            raise ValidationError(result.errors)

        # ... continue with legacy ...

# Comprehensive tests for new class
class TestDataValidator:
    def test_accepts_valid_data(self):
        rules = [
            RequiredFieldRule('id'),
            TypeRule('value', int),
            RangeRule('value', 0, 100)
        ]
        validator = DataValidator(rules)

        result = validator.validate({'id': 123, 'value': 50})

        assert result.is_valid == True
        assert len(result.errors) == 0

    def test_rejects_missing_required_field(self):
        rules = [RequiredFieldRule('id')]
        validator = DataValidator(rules)

        result = validator.validate({'name': 'test'})

        assert result.is_valid == False
        assert 'id is required' in result.errors
```

### Advantages
- ✅ Complete separation from legacy
- ✅ New class is independently testable
- ✅ Clear responsibilities
- ✅ Can evolve independently
- ✅ Reusable in other contexts

### Disadvantages
- ❌ Requires more upfront design
- ❌ May duplicate some legacy functionality
- ❌ Integration point still in untested legacy code

---

## Wrap Method

**When to use:** Need to add logic before or after existing method while preserving original behavior.

**Strategy:** Rename original method and create new public method that wraps both old and new logic.

### Basic Pattern

```python
# BEFORE - Can't test sanitization mixed with export
class DataExporter:
    def export(self, data):
        """Old, working export logic (but untested)"""
        file = open('export.csv', 'w')
        for row in data:
            file.write(','.join(str(v) for v in row.values()))
            file.write('\n')
        file.close()

# AFTER - Wrap with testable preprocessing
class DataExporter:
    def export(self, data):
        """
        Public interface - now wraps sanitization + export.
        Tests cover sanitization; legacy export preserved.
        """
        sanitized = self._sanitize_data(data)
        self._export_original(sanitized)

    def _sanitize_data(self, data):
        """
        New method - fully tested.
        Removes null bytes, strips whitespace, handles None.
        """
        return [
            {k: self._clean_value(v) for k, v in row.items()}
            for row in data
        ]

    def _clean_value(self, value):
        """Clean individual value"""
        if value is None:
            return ''
        return str(value).replace('\x00', '').strip()

    def _export_original(self, data):
        """
        Original logic - renamed, unchanged.
        TODO: Add tests once we have test infrastructure.
        """
        file = open('export.csv', 'w')
        for row in data:
            file.write(','.join(str(v) for v in row.values()))
            file.write('\n')
        file.close()

# Test new sanitization logic
class TestDataExporterSanitization:
    def test_sanitize_removes_null_bytes(self):
        exporter = DataExporter()
        dirty_data = [{'field': 'value\x00with\x00nulls'}]

        result = exporter._sanitize_data(dirty_data)

        assert result[0]['field'] == 'valuewithnulls'

    def test_sanitize_strips_whitespace(self):
        exporter = DataExporter()
        dirty_data = [{'field': '  spaces  '}]

        result = exporter._sanitize_data(dirty_data)

        assert result[0]['field'] == 'spaces'

    def test_sanitize_handles_none(self):
        exporter = DataExporter()
        dirty_data = [{'field': None}]

        result = exporter._sanitize_data(dirty_data)

        assert result[0]['field'] == ''
```

### Wrap Variations

#### Wrap for Logging

```python
class LegacyService:
    def process(self, data):
        """Wrap to add logging"""
        self._log_start(data)
        try:
            result = self._process_original(data)
            self._log_success(result)
            return result
        except Exception as e:
            self._log_error(e)
            raise

    def _log_start(self, data):
        """New, testable logging"""
        logger.info(f"Processing {len(data)} records")

    def _process_original(self, data):
        """Original logic - unchanged"""
        # ... legacy processing ...
```

#### Wrap for Caching

```python
class LegacyCalculator:
    def calculate(self, input_data):
        """Wrap to add caching"""
        cache_key = self._make_cache_key(input_data)
        cached = self._get_from_cache(cache_key)

        if cached is not None:
            return cached

        result = self._calculate_original(input_data)
        self._save_to_cache(cache_key, result)
        return result

    def _make_cache_key(self, data):
        """New, testable cache key generation"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _calculate_original(self, input_data):
        """Original calculation - unchanged"""
        # ... legacy logic ...
```

#### Wrap for Error Handling

```python
class LegacyAPI:
    def call_external_service(self, params):
        """Wrap to add retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return self._call_original(params)
            except NetworkError as e:
                if attempt < max_retries - 1:
                    self._handle_retry(attempt, e)
                else:
                    raise

    def _handle_retry(self, attempt, error):
        """New, testable retry logic"""
        wait_time = 2 ** attempt  # Exponential backoff
        logger.warning(f"Retry {attempt + 1} after {wait_time}s: {error}")
        time.sleep(wait_time)

    def _call_original(self, params):
        """Original API call - unchanged"""
        # ... legacy network call ...
```

### Advantages
- ✅ Preserves original logic exactly
- ✅ New functionality is testable
- ✅ Clear what's new vs. legacy
- ✅ Easy to remove wrapper later

### Disadvantages
- ❌ Method names become verbose (`_original`)
- ❌ Doesn't make legacy code testable
- ❌ Can hide the legacy code's problems

---

## Choosing Between Sprout and Wrap

| Situation | Use Sprout | Use Wrap |
|-----------|------------|----------|
| Adding new feature | ✅ Sprout Method/Class | |
| Adding preprocessing | | ✅ Wrap Method |
| Adding postprocessing | | ✅ Wrap Method |
| Adding error handling | | ✅ Wrap Method |
| Adding logging/metrics | | ✅ Wrap Method |
| Complex new logic | ✅ Sprout Class | |
| Simple new logic | ✅ Sprout Method | |
| Preserving exact behavior | | ✅ Wrap Method |

---

## Advanced Patterns

### Sprout Class with Interface

```python
# Define interface for new functionality
class Validator(Protocol):
    def validate(self, data: dict) -> ValidationResult: ...

# Sprout class implementing interface
class EmailValidator:
    def validate(self, data: dict) -> ValidationResult:
        # Testable validation logic
        pass

# Legacy code depends on interface
class LegacyUserService:
    def __init__(self, validator: Validator = None):
        self.validator = validator or EmailValidator()

    def create_user(self, user_data):
        # ... legacy code ...
        result = self.validator.validate(user_data)
        # ... more legacy ...
```

### Wrap with Decorator

```python
def timing_wrapper(method):
    """Decorator to wrap with timing logic"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        try:
            result = method(self, *args, **kwargs)
            elapsed = time.time() - start
            self._log_timing(method.__name__, elapsed)
            return result
        except Exception as e:
            elapsed = time.time() - start
            self._log_error(method.__name__, elapsed, e)
            raise

    return wrapper

class LegacyService:
    @timing_wrapper
    def process(self, data):
        """Legacy method - wrapped with decorator"""
        # ... untested legacy code ...

    def _log_timing(self, method, elapsed):
        """New, testable logging"""
        logger.info(f"{method} took {elapsed:.2f}s")
```

---

## Common Mistakes

### Mistake 1: Sprouting Too Much

**Problem:** Creating dozens of tiny methods

**Solution:** If you have 5+ sprout methods, consider sprouting a class instead:

```python
# Too many sprout methods
class Processor:
    def process(self):
        self._validate_input()
        self._sanitize_data()
        self._check_permissions()
        self._apply_transforms()
        self._save_results()

# Better: Sprout a class
class ProcessingPipeline:
    def run(self, data):
        self.validate_input(data)
        self.sanitize_data(data)
        # ... all testable ...

class Processor:
    def process(self, data):
        pipeline = ProcessingPipeline()
        return pipeline.run(data)
```

### Mistake 2: Sprouting What Should Be Parameterized

**Problem:** Using sprout when dependency injection would work

```python
# Sprout method for database access
class Service:
    def _get_user(self, user_id):
        """Sprouted method"""
        db = PostgresDB()
        return db.query(...)

# Better: Parameterize constructor
class Service:
    def __init__(self, db=None):
        self.db = db or PostgresDB()

    def get_user(self, user_id):
        return self.db.query(...)
```

### Mistake 3: Not Testing Before Integration

**Problem:** Writing sprout method, integrating it, then trying to test

**Solution:** Test FIRST, integrate second:

```python
# 1. Write sprout method
def _validate_format(self, data):
    return all(required in data for required in ['id', 'type'])

# 2. Write tests
def test_validate_format_accepts_valid():
    obj = MyClass()
    assert obj._validate_format({'id': 1, 'type': 'A'}) == True

def test_validate_format_rejects_invalid():
    obj = MyClass()
    assert obj._validate_format({'id': 1}) == False

# 3. THEN integrate into legacy code
def legacy_method(self, data):
    # ... legacy code ...
    if not self._validate_format(data):  # Now tested!
        raise ValueError()
    # ... more legacy ...
```

---

## Integration with Other Techniques

### Sprout + Characterization Tests

```python
# 1. Write characterization tests for legacy
@pytest.mark.characterization
def test_legacy_behavior():
    result = legacy_function(input)
    assert result == observed_output

# 2. Sprout new testable method
def new_feature(data):
    # Fully tested new code
    pass

# 3. Integrate and verify characterization tests still pass
def legacy_function(input):
    new_data = new_feature(input)  # Added
    # ... rest of legacy unchanged ...
```

### Wrap + Dependency Breaking

```python
# 1. Wrap to add new functionality
class Service:
    def process(self, data):
        validated = self._validate(data)  # New, wrapped
        return self._process_original(validated)

# 2. Then break dependencies in original
class Service:
    def __init__(self, db=None):  # Dependency injection added
        self.db = db or ProductionDB()

    def _process_original(self, data):
        return self.db.query(...)  # Now testable!
```

---

## Quick Reference

**Sprout Method:**
- Small new feature
- Extract as separate method
- Test before integrating

**Sprout Class:**
- Substantial new feature
- Create independent class
- Design for testability

**Wrap Method:**
- Add before/after logic
- Rename original to `_original`
- New wrapper is public interface

**Remember:** Sprout and Wrap are **bridging techniques**. Use them to add testable code to legacy systems, then gradually refactor the legacy parts under test coverage.
