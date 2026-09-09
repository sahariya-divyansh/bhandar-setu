# Contributing to Bhandar Setu

Thank you for your interest in contributing to **Bhandar Setu**. This document outlines the guidelines and workflow for contributing code, documentation, and operational improvements to the platform.

---

## 🛠️ Development Workflow

### 1. Branching Strategy
We follow a standard Feature Branch workflow:
- `main`: Production-ready code. All commits to `main` must pass CI/CD checks.
- `feature/<short-description>`: New features or component additions.
- `fix/<issue-number>-<short-description>`: Bug fixes and security patches.
- `docs/<short-description>`: Documentation updates.

### 2. Local Setup
Ensure both Node.js (v18+) and Python (v3.11+) are installed. Follow setup instructions in the root [`README.md`](README.md).

### 3. Commit Message Conventions
We adhere to Conventional Commits:
```text
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

#### Allowed Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semi-colons, etc (no functional code changes)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance optimizations
- `test`: Adding or correcting tests
- `chore`: Build process or auxiliary tool updates

#### Examples:
```text
feat(backend): add stock-out prediction endpoint with threshold filtering
fix(frontend): resolve re-render loop on inventory dashboard chart
docs(infra): update Cloud Run deployment environment variable reference
```

---

## 📐 Code Standards

### Python (`/backend` and `/ml`)
- Code must follow **PEP 8** standards.
- Type annotations are required for all function parameters and return values.
- Use `black` for code formatting and `flake8` for linting.
- Async endpoints must handle exceptions explicitly and use appropriate HTTP status codes.

### TypeScript / React (`/frontend`)
- Strict mode is enabled (`strict: true` in `tsconfig.json`).
- Prefer Functional Components with explicit React hooks.
- Use named exports for components and utility functions.
- Ensure all interactive UI elements include proper accessibility attributes (`aria-label`, etc.).

---

## 🧪 Testing Guidelines

Before submitting a Pull Request, ensure:
1. Backend unit and integration tests pass:
   ```bash
   cd backend
   pytest
   ```
2. Frontend builds cleanly without TypeScript or lint warnings:
   ```bash
   cd frontend
   npm run build
   ```

---

## 📥 Submitting a Pull Request (PR)

1. Rebase your branch onto the latest `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
2. Open a Pull Request targeting `main`.
3. Provide a clear description of changes, linked issues, and manual verification steps.
4. Obtain code review approval from a maintainer before merging.
