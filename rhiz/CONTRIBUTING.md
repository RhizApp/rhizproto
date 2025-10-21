# Contributing to Rhiz Protocol

Thank you for your interest in contributing to Rhiz Protocol! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** following our guidelines
5. **Test your changes** thoroughly
6. **Submit a pull request**

## Development Setup

See [Installation Guide](apps/docs/docs/getting-started/installation.md) for detailed setup instructions.

Quick start:
```bash
git clone https://github.com/your-username/rhiz.git
cd rhiz
make install
make dev
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(api): add trust decay algorithm
fix(web): resolve dashboard loading issue
docs(protocol): update relationship schema
test(sdk): add pathfinding tests
chore(deps): upgrade dependencies
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

**Scopes:**
- `api`, `web`, `atproto`, `docs`, `protocol`, `sdk-ts`, `sdk-py`, `shared`, `ci`, `deps`, `config`

## Code Style

### TypeScript/JavaScript
- Use Prettier for formatting
- Follow ESLint rules
- Write meaningful variable names
- Add JSDoc comments for public APIs

```typescript
/**
 * Calculate trust score for an entity
 * @param entityId - Entity identifier
 * @returns Trust score between 0 and 1
 */
export function calculateTrustScore(entityId: string): Promise<number> {
  // Implementation
}
```

### Python
- Use Black for formatting
- Follow Ruff linting rules
- Use type hints
- Add docstrings for functions

```python
def calculate_trust_score(entity_id: str) -> float:
    """
    Calculate trust score for an entity.

    Args:
        entity_id: Entity identifier

    Returns:
        Trust score between 0.0 and 1.0
    """
    # Implementation
```

## Testing

All new code must include tests:

```bash
# TypeScript tests
pnpm test

# Python tests
cd apps/api && poetry run pytest

# Run all tests
make test
```

**Test Coverage Requirements:**
- Backend: 80%+
- Frontend: 70%+
- SDKs: 90%+

## Pull Request Process

1. **Update documentation** if you change APIs
2. **Add tests** for new features
3. **Run linters** and fix any issues
4. **Update CHANGELOG.md** with your changes
5. **Request review** from maintainers

### PR Title Format
```
feat(api): add relationship decay detection

- Implement time-based strength decay
- Add configuration for decay rates
- Include tests for all relationship types

Closes #123
```

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] No breaking changes (or clearly documented)

## Project Structure

```
rhiz/
├── apps/           # Applications
│   ├── api/       # FastAPI backend
│   ├── web/       # Next.js frontend
│   ├── atproto/   # AT Protocol services
│   └── docs/      # Documentation site
├── packages/       # Shared packages
│   ├── protocol/  # Core protocol types
│   ├── sdk-ts/    # TypeScript SDK
│   └── sdk-py/    # Python SDK
└── scripts/        # Development scripts
```

## Branch Strategy

- `main` - Stable, production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `docs/*` - Documentation updates

## Release Process

1. Create release branch from `develop`
2. Update version numbers
3. Update CHANGELOG.md
4. Create PR to `main`
5. Tag release after merge
6. Publish to npm/PyPI

## Need Help?

- **Discord**: [Join our community](https://discord.gg/rhiz)
- **Issues**: [GitHub Issues](https://github.com/rhiz/rhiz/issues)
- **Email**: team@rhiz.network

## License

By contributing, you agree that your contributions will be licensed under MIT and Apache 2.0 licenses.

