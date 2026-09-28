# Contributing

## Branches

Use the following naming conventions:

- `feat/<name>` for new functionality
- `fix/<name>` for bug fixes
- `data/<name>` for dataset work
- `exp/<name>` for experiments
- `docs/<name>` for documentation

## Workflow

1. Update or create the relevant specification.
2. Create a feature branch from `dev`.
3. Implement the tasks defined by the specification.
4. Run local checks.
5. Commit the changes.
6. Push the branch.
7. Open a pull request into `dev`.
8. Request teammate review.
9. Address review comments.
10. Merge only after required checks pass.

## Commits

Use concise, imperative commit messages. Conventional prefixes such as
`feat:`, `fix:`, `docs:`, and `chore:` are encouraged.

## Pull requests and review

Open pull requests against `dev`. Explain the change, note relevant validation,
and link related issues or specifications. Request at least one teammate review,
address review comments, and merge only after approval and required checks pass.

## Local checks

For Python project changes, synchronize the environment and run the test suite:

```sh
uv sync
uv run pytest
```

Keep datasets, model outputs, credentials, and local environment files out of
Git. Update this guide when the project's required checks change.
