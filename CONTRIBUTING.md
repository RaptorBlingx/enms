# Contributing to EnMS

Thank you for your interest in contributing to EnMS! This document provides guidelines for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/enms.git
   cd enms
   ```
3. **Set up the development environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ./setup.sh
   ```

## Development Workflow

### Branch Naming

- `feature/` - New features (e.g., `feature/add-carbon-tracking`)
- `fix/` - Bug fixes (e.g., `fix/anomaly-detection-threshold`)
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### Making Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Write tests for new functionality

4. Run the test suite:
   ```bash
   docker-compose exec analytics pytest tests/ -v
   docker-compose exec query-service pytest tests/ -v
   ```

5. Commit your changes with meaningful messages:
   ```bash
   git commit -m "feat: add carbon emission tracking to KPI dashboard"
   ```

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Code Style Guidelines

### Python (FastAPI Services)

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Use Pydantic models for request/response validation
- Keep functions focused and under 50 lines where possible

### SQL

- Use parameterized queries (prevent SQL injection)
- Use TimescaleDB continuous aggregates for time-series queries
- Follow the existing naming conventions (snake_case for tables/columns)

### JavaScript/CSS

- Use modern ES6+ syntax
- Follow existing patterns in portal code

## Testing

- All new features must include tests
- Maintain or improve code coverage
- Test edge cases and error handling

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update the README if you're adding new features
4. Request review from maintainers
5. Address review feedback

## Questions?

Open an issue on GitHub or reach out to the maintainers.

Thank you for contributing! 🙏
