# Characterization Testing

Characterization tests document **what code currently does**, not what it **should** do. Use them when you don't fully understand legacy code but need to change it safely.

---

## Purpose

Characterization tests serve as a safety net during refactoring by:
1. **Preserving behavior** - Catch unintended changes
2. **Documenting behavior** - Record what code actually does
3. **Building confidence** - Enable safe refactoring
4. **Finding bugs** - Sometimes reveal unexpected behavior

---

## When to Use

Use characterization tests when:
- ✅ Code behavior is unclear or undocumented
- ✅ Preparing to refactor complex logic
- ✅ No existing tests cover the code
- ✅ Too risky to change without a safety net
- ✅ Code works in production but you don't know why

Don't use when:
- ❌ Behavior is well-documented and understood
- ❌ Code is already covered by good tests
- ❌ You're writing new code (use TDD instead)

---

## The Process

### Step 1: Run the Code

Execute the legacy function with various inputs and observe outputs.

```python
# Legacy function - behavior unclear
def calculate_shipping_cost(weight, distance, customer_type):
    # ... 100 lines of mysterious logic ...
    return cost

# Experiment: Run with different inputs
print(calculate_shipping_cost(10, 100, 'standard'))  # 15.50
print(calculate_shipping_cost(10, 100, 'premium'))   # 12.40
print(calculate_shipping_cost(50, 500, 'standard'))  # 87.25
print(calculate_shipping_cost(0, 0, 'standard'))     # 5.00 (minimum charge?)
```

### Step 2: Document Observations

Write tests that capture observed behavior:

```python
@pytest.mark.characterization
@pytest.mark.parametrize("weight,distance,customer_type,expected", [
    (10, 100, 'standard', 15.50),
    (10, 100, 'premium', 12.40),
    (50, 500, 'standard', 87.25),
    (0, 0, 'standard', 5.00),      # Edge case: minimum charge
    (1000, 5000, 'vip', 450.00),  # Edge case: large shipment
])
def test_calculate_shipping_cost_characterization(weight, distance, customer_type, expected):
    """
    Characterization test for calculate_shipping_cost.

    Captures current behavior observed on 2025-01-20.
    Values verified against production logs.

    TODO: Review if behavior is correct once business logic is understood.
    Then refactor with confidence knowing tests will catch changes.
    """
    result = calculate_shipping_cost(weight, distance, customer_type)
    assert result == pytest.approx(expected, rel=0.01)
```

### Step 3: Cover Edge Cases

Find boundary conditions and unusual inputs:

```python
@pytest.mark.characterization
def test_calculate_shipping_cost_edge_cases():
    """Edge cases discovered during characterization"""

    # Negative values - what happens?
    assert calculate_shipping_cost(-10, 100, 'standard') == 5.00  # Treats as zero?

    # Invalid customer type
    with pytest.raises(ValueError):
        calculate_shipping_cost(10, 100, 'invalid')

    # Very large values
    assert calculate_shipping_cost(10000, 10000, 'standard') > 1000  # Scales up

    # Zero distance
    assert calculate_shipping_cost(100, 0, 'standard') == 5.00  # Min charge applies
```

### Step 4: Refactor Under Coverage

Now you can refactor safely:

```python
def calculate_shipping_cost(weight, distance, customer_type):
    """
    REFACTORED VERSION - Tests ensure behavior preserved

    Business logic (discovered through characterization):
    - Minimum charge: $5.00
    - Base rate: $0.05/lb
    - Distance factor: $0.02/mile
    - Premium customers: 20% discount
    - VIP customers: 50% discount
    """
    # Refactored code here
    # Tests will catch if behavior changes!
```

---

## Patterns and Techniques

### Pattern 1: Parametrized Characterization

Use `pytest.mark.parametrize` to cover many cases concisely:

```python
@pytest.mark.characterization
@pytest.mark.parametrize("input_data,expected_output", [
    ({'status': 'active', 'age': 25}, True),
    ({'status': 'inactive', 'age': 25}, False),
    ({'status': 'pending', 'age': 17}, False),
    # ... 20 more cases from production logs
])
def test_is_eligible_characterization(input_data, expected_output):
    """Captures is_eligible behavior from production"""
    assert is_eligible(input_data) == expected_output
```

### Pattern 2: Golden Master Testing

Save complex output and compare future runs against it:

```python
import json
from pathlib import Path

@pytest.mark.characterization
def test_generate_report_golden_master(tmp_path):
    """Golden master test - preserves exact output"""

    # Run the legacy function
    result = generate_complex_report(sample_data)

    # First run: Save the output
    golden_file = Path('tests/golden_masters/report_output.json')
    if not golden_file.exists():
        golden_file.write_text(json.dumps(result, indent=2))
        pytest.skip("Golden master created - review and commit it")

    # Subsequent runs: Compare against golden master
    expected = json.loads(golden_file.read_text())
    assert result == expected, "Output differs from golden master!"
```

### Pattern 3: Exception Characterization

Document what exceptions are raised:

```python
@pytest.mark.characterization
def test_validate_input_exceptions():
    """Characterize exception behavior"""

    # ValueError for negative numbers
    with pytest.raises(ValueError, match="must be positive"):
        validate_input(-1)

    # TypeError for non-numeric input
    with pytest.raises(TypeError):
        validate_input("not a number")

    # No exception for valid input
    validate_input(42)  # Should not raise
```

### Pattern 4: State Characterization

Capture side effects and state changes:

```python
@pytest.mark.characterization
def test_update_user_side_effects():
    """Characterize state changes and side effects"""

    user = User(id=1, status='pending', updated_count=0)

    # Call the legacy method
    legacy_update_user(user, {'status': 'active'})

    # Document observed state changes
    assert user.status == 'active'
    assert user.updated_count == 1  # Side effect: increments counter
    assert user.last_updated is not None  # Side effect: sets timestamp
```

---

## Best Practices

### Use Descriptive Test Names

```python
# Bad
def test_calc_1():
    pass

# Good
def test_calculate_discount_returns_10_percent_for_premium_customers_with_5_items():
    pass
```

### Add Context Comments

```python
@pytest.mark.characterization
def test_legacy_pricing_algorithm():
    """
    Characterization test for legacy pricing algorithm.

    Observed behavior on 2025-01-20 from production logs.

    Discovered quirks:
    - Rounds to nearest $0.25 increment
    - Minimum price is $1.00 regardless of input
    - Negative prices treated as zero

    TODO: Verify with business team if this is correct
    """
    # tests here
```

### Mark as Characterization

```python
@pytest.mark.characterization  # Easy to find/filter characterization tests
def test_legacy_behavior():
    pass
```

### Separate from Unit Tests

```python
tests/
├── unit/                    # True unit tests
│   └── test_new_code.py
├── characterization/        # Characterization tests
│   ├── test_legacy_calculator.py
│   └── test_legacy_formatter.py
└── integration/
    └── test_pipeline.py
```

---

## Common Pitfalls

### Pitfall 1: Testing Too Much at Once

**Problem:**
```python
def test_entire_system():
    # Trying to characterize 10,000 lines in one test
    result = run_entire_legacy_system(input)
    assert result == huge_expected_output
```

**Solution:** Break into smaller chunks:
```python
def test_step1_parsing():
    result = parse_input(raw_data)
    assert result == expected_parsed

def test_step2_validation():
    result = validate(parsed_data)
    assert result == expected_validated
```

### Pitfall 2: Assuming Correctness

**Problem:** Codifying bugs as "correct behavior"

**Solution:** Mark uncertain behavior:
```python
def test_suspicious_behavior():
    """
    Characterization test - preserves current behavior.

    WARNING: This might be a bug!
    - Returns negative value for positive input
    - Inconsistent with similar function foo()
    - TODO: Verify with product team
    """
    assert weird_function(5) == -10  # Preserving even if wrong
```

### Pitfall 3: Not Covering Edge Cases

**Problem:** Only testing happy path

**Solution:** Systematically test boundaries:
```python
@pytest.mark.parametrize("input_value", [
    -1,      # Below minimum
    0,       # Minimum boundary
    1,       # Just above minimum
    999,     # Just below maximum
    1000,    # Maximum boundary
    1001,    # Above maximum
    None,    # Null
    '',      # Empty
])
def test_edge_cases_characterization(input_value):
    # Document behavior at boundaries
    result = legacy_function(input_value)
    # assert based on observed behavior
```

---

## Example: Full Characterization Workflow

```python
# STEP 1: Identify legacy code
def calculate_tax(amount, state, customer_type):
    # ... 150 lines of mysterious tax calculation ...
    return tax_amount

# STEP 2: Experiment and observe
"""
Manual testing revealed:
- CA: 8.5% tax for regular, 7.0% for wholesale
- NY: 4.0% tax for regular, 3.5% for wholesale
- TX: 6.25% tax for all
- Negative amounts return 0
- Unknown states raise ValueError
"""

# STEP 3: Write characterization tests
@pytest.mark.characterization
class TestCalculateTaxCharacterization:
    """Characterization tests for legacy tax calculator"""

    @pytest.mark.parametrize("amount,state,customer_type,expected", [
        # California cases
        (100, 'CA', 'regular', 8.50),
        (100, 'CA', 'wholesale', 7.00),
        # New York cases
        (100, 'NY', 'regular', 4.00),
        (100, 'NY', 'wholesale', 3.50),
        # Texas cases (no wholesale discount)
        (100, 'TX', 'regular', 6.25),
        (100, 'TX', 'wholesale', 6.25),
        # Edge cases
        (0, 'CA', 'regular', 0),
        (-100, 'CA', 'regular', 0),
    ])
    def test_tax_calculation(self, amount, state, customer_type, expected):
        """Tax calculation behavior observed 2025-01-20"""
        result = calculate_tax(amount, state, customer_type)
        assert result == pytest.approx(expected, abs=0.01)

    def test_unknown_state_raises_error(self):
        """Unknown states raise ValueError"""
        with pytest.raises(ValueError, match="Unknown state"):
            calculate_tax(100, 'ZZ', 'regular')

# STEP 4: Refactor with confidence
def calculate_tax(amount, state, customer_type):
    """
    REFACTORED - behavior preserved by characterization tests

    Tax rates discovered through characterization:
    - CA: 8.5% (7.0% wholesale)
    - NY: 4.0% (3.5% wholesale)
    - TX: 6.25% (no wholesale discount)
    """
    if amount < 0:
        return 0

    rates = {
        'CA': {'regular': 0.085, 'wholesale': 0.070},
        'NY': {'regular': 0.040, 'wholesale': 0.035},
        'TX': {'regular': 0.0625, 'wholesale': 0.0625},
    }

    if state not in rates:
        raise ValueError(f"Unknown state: {state}")

    rate = rates[state][customer_type]
    return amount * rate
```

---

## Quick Reference

**When characterizing:**
1. Run code with diverse inputs
2. Record observed outputs
3. Cover edge cases and exceptions
4. Mark tests with `@pytest.mark.characterization`
5. Add context comments
6. **Don't assume correctness** - document what it does, not what it should do

**After characterizing:**
- Review behavior with domain experts
- Refactor with test coverage
- Gradually replace characterization tests with proper unit tests
- Keep characterization tests until refactoring is complete

**Remember:** Characterization tests are **temporary scaffolding**. Once you understand and refactor the code, replace them with proper unit tests that describe correct behavior.
