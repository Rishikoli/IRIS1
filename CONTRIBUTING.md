# Contributing to I.R.I.S.

First off, thank you for considering contributing to I.R.I.S. (Investigative Risk Intelligence System)! It's people like you that make such tools powerful and effective.

## 🤝 Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/your-username/IRIS1.git
    cd IRIS1
    ```
3.  **Set up the environment** following the [Installation Guide](./README.md#installation-guide) in the README.

## 🛠 Development Workflow

1.  **Create a Branch**: Always work on a new branch for your feature or fix.
    ```bash
    git checkout -b feature/amazing-new-feature
    # or
    git checkout -b fix/critical-bug-fix
    ```
2.  **Commit Changes**: Make sure your commit messages are clear and descriptive.
    *   Good: `feat: Add new SEBI compliance check for Related Party Transactions`
    *   Bad: `update code`
3.  **Keep it Sync**: Regularly pull upstream changes to avoid conflicts.
    ```bash
    git pull origin master
    ```

## 📐 Coding Standards

### Backend (Python)
*   Follow **PEP 8** style guidelines.
*   Use **Type Hints** for function arguments and return values.
*   Run the linter before pushing:
    ```bash
    flake8 .
    ```

### Frontend (Next.js / TypeScript)
*   Use **functional components** and hooks.
*   Ensure all components are strictly typed.
*   Follow the existing folder structure (`src/components`, `src/app`).
*   Use Tailwind CSS for styling (avoid inline styles).

## 🚀 Pull Request Process

1.  Push your branch to GitHub.
2.  Open a Pull Request against the `master` branch.
3.  Fill out the PR template describing your changes, why they are necessary, and how to test them.
4.  Wait for review! We aim to review all PRs within 48 hours.

## 🐞 Reporting Bugs

If you find a bug, please create an issue with:
*   A descriptive title.
*   Steps to reproduce the issue.
*   Expected vs. actual behavior.
*   Screenshots or logs if applicable.

Thank you for helping us make financial markets safer and more transparent!
