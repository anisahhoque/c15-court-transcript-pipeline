# Court Transcript Pipeline Code Quality Guide

## General Note

This code quality guide is intended to ensure consistent, maintainable, and readable code across the Cour Transcript Pipeline project. For Python-specific guidance, conflicts between this document and PEP standards (e.g., [PEP 8](https://peps.python.org/pep-0008/)) should defer to PEP, and an issue should be created to resolve any ambiguities.

This guide supplements and extends the project’s [Style Guide](./STYLE_GUIDE.md) to provide more explicit quality requirements.

---

## Code Review Standards

- All pull requests must pass automated testing before merging. This includes:

  - Running all `pytest` scripts successfully, ensuring no failed tests.
  - Meeting a minimum `pylint` score of 9 across all affected Python modules.
- **Two Successful peer reviews** are required for merging pull requests to main and these reviews must focus on:

  - Adherence to this guide and the style guide.
  - Logic correctness (e.g., does the code do what it's supposed to?).
  - Code maintainability (e.g., is the logic easy to understand, debug, and extend?).
  - Avoidance of unnecessary complexity or duplication.

---

## Documentation and Comments

- **Docstrings**: Every function and class should have a docstring explaining its purpose. Follow [PEP 257](https://peps.python.org/pep-0257/) for formatting and conventions.

  - Include parameter descriptions, return types, and side effects (if applicable).
  - Use concise descriptions.
- **Inline Comments**: Avoid unnecessary comments. Use inline comments sparingly for non-obvious logic, following the guidelines in [PEP 8](https://peps.python.org/pep-0008/).

---

## Function returns

- Functions should only return one type of object
- Where functions fail, they should always raise an exception
- All exceptions should include a terse description of what went wrong

---

## Testing

- **Coverage**: Maintain at least **90% overall test coverage** across the codebase. Critical functions (e.g., core logic) should aim for **100% coverage**, including edge cases.
- Use `pytest-cov` for measuring coverage:  `--cov=my_project`
- **New Code**:

  - All new features must include sufficient tests to meet the coverage targets.
  - Bug fixes should include "regression tests" to prevent reintroducing the issue.
- **Structure**: Tests must follow the "AAA" pattern:

  1. **Arrange**: Set up the necessary data or environment.
  2. **Act**: Perform the operation being tested.
  3. **Assert**: Verify the expected results.

---

## Performance

- Use appropriate data structures for efficiency, e.g:

  - **Dictionaries (`dict`)** for key-value lookups.
  - **Sets (`set`)** for membership checks.
  - **Tuples (`tuple`)** for immutable sequences when order matters but modifications are unnecessary.
- Avoid unnecessary loops:

  - Use **list/set/dictionary comprehensions** instead of loops where appropriate.
- Cache expensive computations when possible.

---

## Security

- Avoid hardcoding sensitive information. Use environment variables or a secrets manager.
- Validate and sanitise all input to avoid injection attacks or unexpected behaviour. (e.g. no f-strings should be used within SQL queries)

---

## Code Quality Metrics

- **Function Length**: Functions should generally not exceed 50 lines.
- **Pylint Score**: A minimum score of 9 is required for all Python modules.

---
