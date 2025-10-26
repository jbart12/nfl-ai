# Contributing Guidelines

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd nfl-ai

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### 2. Code Standards

**Type Hints**:
- All functions must have type hints
- Use `mypy` to verify type safety

**Documentation**:
- All modules must have docstrings
- All classes must have docstrings
- All public functions must have docstrings with Args, Returns, Examples

**Formatting**:
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### 3. Testing Requirements

**Before committing**:
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit           # Fast unit tests
pytest -m integration    # Integration tests
pytest -m e2e           # End-to-end tests

# Check coverage
pytest --cov-report=html
```

**Test Coverage Requirements**:
- Unit tests: 90%+ coverage
- Integration tests: 80%+ coverage
- All new code must include tests

### 4. Adding a New Data Source

Follow the **Data Source Accessor Pattern**:

1. **Create module structure**:
```
src/data/accessors/newsource/
├── __init__.py
├── accessor.py      # Main accessor class
├── client.py        # HTTP client
├── parser.py        # Response parsing
├── models.py        # Data models
└── cache.py         # Caching (optional)
```

2. **Implement BaseDataAccessor**:
```python
from src.data.accessors.base import BaseDataAccessor

class NewSourceAccessor(BaseDataAccessor):
    async def connect(self) -> None:
        # Implementation
        pass

    async def fetch_player_data(self, player_id: int) -> Dict:
        # Implementation
        pass
```

3. **Write comprehensive tests**:
```python
# tests/unit/data/test_newsource_accessor.py
async def test_fetch_player_data(mock_client):
    # Test implementation
    pass
```

4. **Document thoroughly**:
- Create `docs/sources/NEWSOURCE_API.md`
- Add sample responses to `samples/newsource/`
- Update `README.md` data sources list

### 5. Git Workflow

**Branch Naming**:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `test/description` - Test improvements

**Commit Messages**:
```
type(scope): short description

Longer description if needed.

- Bullet points for details
- What changed and why
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`

**Pull Request Process**:
1. Create feature branch
2. Write code + tests
3. Run full test suite
4. Update documentation
5. Create PR with description
6. Address review comments
7. Merge when approved

### 6. Code Review Checklist

Reviewer should verify:
- [ ] Code follows architectural patterns
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Tests are comprehensive
- [ ] Test coverage > 90%
- [ ] Documentation is updated
- [ ] No hardcoded secrets
- [ ] Error handling is appropriate
- [ ] Logging is appropriate

### 7. Documentation Standards

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed examples.

**Module Docstring Template**:
```python
"""
Module Name

Brief description of what this module does.

Components:
    - ClassA: Description
    - ClassB: Description

Usage:
    from module import ClassA
    obj = ClassA()
    obj.method()

Notes:
    Any important notes
"""
```

**Function Docstring Template**:
```python
def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
    """
    Brief description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ErrorType: When this error occurs

    Example:
        >>> function_name("value", 123)
        "result"

    Notes:
        Additional notes
    """
```

### 8. Performance Guidelines

- Use `async/await` for I/O operations
- Implement caching for frequently accessed data
- Use connection pooling for databases
- Batch API requests when possible
- Monitor and log slow operations (>1s)

### 9. Security Guidelines

- Never commit API keys or secrets
- Use `.env` for configuration
- Validate all external input
- Use parameterized queries
- Implement rate limiting
- Log security-relevant events

### 10. Questions?

- Check [ARCHITECTURE.md](ARCHITECTURE.md)
- Check [README.md](README.md)
- Check existing code examples
- Open an issue for discussion
