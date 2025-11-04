# Contributing to ETA Tracker

Thank you for considering contributing to the ETA Tracker project! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

## 📜 Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/eta_tracker.git
   cd eta_tracker
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/eta_tracker.git
   ```
4. **Install dependencies**:
   ```bash
   # Frontend
   npm install
   
   # Backend
   pip install -r requirements.txt
   ```
5. **Set up environment variables** by copying `.env.example` to `.env`
6. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔄 Development Workflow

1. **Keep your fork synced** with upstream:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Make your changes** in your feature branch

3. **Test your changes** thoroughly (see Testing section)

4. **Commit your changes** following our commit guidelines

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** from your fork to the main repository

## 💻 Coding Standards

### TypeScript/React

- Use **TypeScript** for all new React components
- Follow **functional component** patterns with hooks
- Add **JSDoc comments** for all functions and components
- Use **meaningful variable names** that describe purpose
- Keep components **focused and single-responsibility**
- Use **Tailwind CSS** for styling (avoid inline styles)

Example:
```typescript
/**
 * Format address components into standard string format
 * @param components - Structured address fields
 * @returns Formatted address string
 */
const formatAddress = (components: AddressComponents): string => {
  // Implementation
};
```

### Python/Flask

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and returns
- Add **docstrings** for all functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

Example:
```python
def geocode_address(address: str) -> dict:
    """
    Geocode address using OpenStreetMap Nominatim API.
    
    Args:
        address: Full address string
        
    Returns:
        Dictionary with lat, lon, and display_name
    """
    # Implementation
```

### General Guidelines

- **DRY Principle**: Don't Repeat Yourself
- **SOLID Principles**: Especially Single Responsibility
- **Error Handling**: Always handle potential errors gracefully
- **Comments**: Explain *why*, not *what* (code should be self-documenting)
- **Performance**: Consider performance implications of changes

## 📝 Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no functionality change)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(dashboard): add collapsible sections for address input

Added dropdown functionality to Origin, Destination, and Intermediate Stops
sections to reduce visual clutter. Sections default to collapsed state.

Closes #123
```

```
fix(geocoding): handle rate limiting with exponential backoff

Implemented retry logic with 2-second delays when OpenStreetMap API
returns 429 status. Max 3 retry attempts before failing.
```

## 🔀 Pull Request Process

1. **Update documentation** if you've changed APIs or functionality
2. **Add tests** for new features
3. **Ensure all tests pass** before submitting
4. **Update the README.md** if needed
5. **Fill out the PR template** completely
6. **Request review** from maintainers
7. **Address review feedback** promptly
8. **Squash commits** if requested before merging

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No console errors or warnings
- [ ] Tested in multiple browsers (if frontend)
- [ ] Commits follow commit message guidelines

## 🧪 Testing

### Frontend Testing

```bash
# Run development server
npm run dev

# Build production bundle
npm run build

# Preview production build
npm run preview
```

**Manual Testing Checklist:**
- [ ] All address inputs work correctly
- [ ] Route preview generates without errors
- [ ] Geocoding handles invalid addresses gracefully
- [ ] Map displays correctly with markers and routes
- [ ] Real-time updates work via Socket.io
- [ ] Responsive design works on mobile/tablet

### Backend Testing

```bash
# Run Python tests
python -m pytest

# Run specific test file
python test_backend.py

# Test API endpoints
python test_api.py
```

**Manual Testing Checklist:**
- [ ] All API endpoints return expected responses
- [ ] Database operations complete successfully
- [ ] Socket.io events emit correctly
- [ ] Error handling works for edge cases
- [ ] Geocoding API integration functions properly

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Clear title** describing the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Screenshots** if applicable
5. **Environment details** (OS, browser, Node/Python versions)
6. **Error messages** or console logs

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** clearly and in detail
3. **Explain the use case** and benefits
4. **Provide examples** or mockups if possible
5. **Consider implementation** complexity and scope

## 📞 Questions?

- Open an issue with the `question` label
- Check existing documentation first
- Be specific about what you need help with

---

**Thank you for contributing to ETA Tracker!** 🚀
