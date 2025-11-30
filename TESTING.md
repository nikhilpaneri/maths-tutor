# Testing Guide

Comprehensive testing guide for the Timestable Tutor application.

## Overview

The project includes a full test suite covering:
- **Unit tests** for agents, services, and models
- **Integration tests** for API endpoints
- **Code coverage reporting**
- **Async test support**

## Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures and configuration
│   ├── test_math_tutor_agent.py   # Math Tutor Agent tests
│   ├── test_facts_agent.py        # Facts Agent tests
│   ├── test_memory_service.py     # Memory Service tests
│   └── test_api.py                # API endpoint tests
├── pytest.ini                      # Pytest configuration
└── requirements.txt                # Includes testing dependencies
```

## Prerequisites

Make sure you have the backend dependencies installed:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

## Running Tests

### Option 1: Quick Test Run (Recommended)

Use the provided test runner script:

```bash
./run-tests.sh
```

This script:
- Activates the virtual environment
- Installs test dependencies if needed
- Runs all tests with coverage
- Generates HTML coverage report

### Option 2: Manual Test Run

From the backend directory:

```bash
cd backend
source venv/bin/activate
pytest
```

### Option 3: Run Specific Tests

**Run tests for a specific module:**
```bash
pytest tests/test_math_tutor_agent.py
```

**Run a specific test function:**
```bash
pytest tests/test_math_tutor_agent.py::TestMathTutorAgent::test_generate_question_success
```

**Run tests by marker:**
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m asyncio       # Run only async tests
```

## Test Coverage

### View Coverage in Terminal

Coverage is automatically shown after running tests:

```bash
pytest
```

### Generate HTML Coverage Report

```bash
pytest --cov-report=html
```

Then open `backend/htmlcov/index.html` in your browser:

```bash
open backend/htmlcov/index.html
```

### Check Coverage for Specific Module

```bash
pytest --cov=agents tests/test_math_tutor_agent.py
```

## Writing Tests

### Test Structure

Tests follow this structure:

```python
import pytest
from unittest.mock import Mock, patch

class TestYourComponent:
    """Test suite for YourComponent"""

    @pytest.fixture
    def component(self):
        """Create component instance for testing"""
        return YourComponent()

    def test_something(self, component):
        """Test description"""
        # Arrange
        input_data = "test"

        # Act
        result = component.do_something(input_data)

        # Assert
        assert result == expected_value
```

### Async Tests

For testing async functions:

```python
@pytest.mark.asyncio
async def test_async_function(self, agent):
    """Test async functionality"""
    result = await agent.async_method()
    assert result is not None
```

### Mocking

Use mocks to isolate components:

```python
@patch('module.external_dependency')
def test_with_mock(self, mock_dependency):
    """Test with mocked dependency"""
    mock_dependency.return_value = "mocked value"
    # Your test code here
```

### Fixtures

Shared test data is in `conftest.py`:

```python
@pytest.fixture
def sample_session_data():
    """Provide sample session data"""
    return {
        "session_id": "test-123",
        "student_name": "Test Student",
        "max_timestable": 10
    }
```

## Test Categories

### Unit Tests

Test individual components in isolation:

- **Math Tutor Agent**: Question generation, answer evaluation, adaptive logic
- **Facts Agent**: Fun facts, quizzes, answer checking
- **Memory Service**: Session CRUD, persistence, pause/resume
- **Models**: Data validation and business logic

### Integration Tests

Test multiple components working together:

- **API Endpoints**: Request/response handling, error cases
- **Agent Coordination**: Multi-agent interactions
- **End-to-End Flows**: Complete user journeys

## Continuous Integration

### Running Tests in CI/CD

Add to your CI pipeline:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    cd backend
    source venv/bin/activate
    pytest --cov --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Test Best Practices

### 1. Test One Thing at a Time

```python
# Good
def test_addition():
    assert calculator.add(2, 3) == 5

# Avoid
def test_all_operations():
    assert calculator.add(2, 3) == 5
    assert calculator.subtract(5, 2) == 3
    assert calculator.multiply(2, 3) == 6
```

### 2. Use Descriptive Test Names

```python
# Good
def test_evaluate_answer_marks_correct_when_answer_matches()

# Avoid
def test_answer()
```

### 3. Follow AAA Pattern

```python
def test_something():
    # Arrange - Set up test data
    student_name = "Test"
    max_level = 10

    # Act - Perform the action
    result = create_session(student_name, max_level)

    # Assert - Verify the result
    assert result.student_name == student_name
```

### 4. Test Edge Cases

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculator.divide(10, 0)
```

### 5. Keep Tests Fast

- Mock external dependencies (API calls, database)
- Use in-memory data structures
- Run slow tests separately with markers

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Make sure you're in the backend directory
cd backend

# Make sure PYTHONPATH includes backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to conftest.py (already done)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Async Test Errors

Make sure tests are marked with `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Mock Not Working

Ensure you're patching the right location:

```python
# Patch where it's used, not where it's defined
@patch('agents.math_tutor_agent.genai.Client')  # Correct
# not
@patch('google.genai.Client')  # May not work
```

## Coverage Goals

Target coverage levels:
- **Overall**: 80%+ coverage
- **Agents**: 90%+ coverage
- **Services**: 85%+ coverage
- **API**: 95%+ coverage

## Example Test Output

```
================================ test session starts =================================
platform darwin -- Python 3.9.0, pytest-7.4.0, pluggy-1.0.0
rootdir: /Users/.../timestable-tutor/backend
configfile: pytest.ini
plugins: asyncio-0.21.0, cov-4.1.0
collected 45 items

tests/test_math_tutor_agent.py ........                                        [ 17%]
tests/test_facts_agent.py .......                                              [ 33%]
tests/test_memory_service.py ..........                                        [ 55%]
tests/test_api.py ......................                                       [100%]

---------- coverage: platform darwin, python 3.9.0 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
agents/__init__.py                    3      0   100%
agents/coordinator_agent.py         120      8    93%   45-47, 89
agents/facts_agent.py                95      5    95%   67, 89
agents/math_tutor_agent.py          142      7    95%   78, 134
models/__init__.py                    2      0   100%
models/student.py                    45      2    96%   34, 56
services/__init__.py                  0      0   100%
services/memory_service.py           78      4    95%   45, 67
utils/__init__.py                     0      0   100%
utils/logging_config.py              89     12    87%   45-48, 78-82
---------------------------------------------------------------
TOTAL                               574     38    93%

================================ 45 passed in 3.45s ==================================
```

## Next Steps

After running tests successfully:

1. **Review coverage report** - Identify untested code
2. **Add more tests** - Cover edge cases
3. **Integrate with CI** - Automate testing
4. **Monitor test performance** - Keep tests fast

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

## Support

For issues with tests:
1. Check test output for error details
2. Review `pytest.ini` configuration
3. Ensure all dependencies are installed
4. Check Python version compatibility (3.9+)

Happy Testing! 🧪
