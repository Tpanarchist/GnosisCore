# Testing Instructions

This guide explains how to run, write, and extend tests for GnosisCore.

## Running Tests

All tests are located in the `tests/` directory and use Python's built-in `unittest` framework.

To run all tests:
```sh
python -m unittest discover tests
```

To run a specific test file:
```sh
python -m unittest tests/test_tick.py
```

## Writing Tests

- Place new test files in the `tests/` directory.
- Name test files with the `test_*.py` pattern.
- Use the `unittest.TestCase` class for test cases.
- Write descriptive test method names and docstrings.

Example:
```python
import unittest
from gnosiscore.patterns.memory import MemoryPattern

class TestMemoryPattern(unittest.TestCase):
    def test_store_and_recall(self):
        memory = MemoryPattern()
        memory.store("key", "value")
        self.assertEqual(memory.recall("key"), "value")
```

## Testing Strategy

- Cover core logic, edge cases, and error handling.
- Add tests for new features and bug fixes.
- Keep tests isolated and independent.

## Continuous Integration

- Ensure all tests pass before submitting a pull request.
- Automated test runs are recommended for CI/CD pipelines.

---

For more details, see the [Module Reference](modules.md) and [Contribution Guidelines](contributing.md).
