---
layout: page
title: Continous Integration
category: Developer
---

# Checks

Before a branch can be merged into master, it must pass all continuous integration test of which there are quite many.

CI has a testing and a linting part:

### Testing

Defined in `CLST-2020/.github/workflows/codecov.yaml`.

1. Set up job: sets up a virtual environment to run checks in
2. Checkout repository
3. Setup Python
4. Install poetry: Update installed packages and install poetry
5. Restore any cached Poetry dependencies
6. Install any new dependencies: runs `poetry install`.
7. Test migrations: tests if migrations can be applied without issue
8. Check server: runs `manage.py check`
9. Run Django tests using coverage: runs all tests giving coverage output
10. Check Coverage report: display report in CI console
11. Generate a coverage xml
12. Run Codecov.io: upload xml file to codecov


### Linting

Defined in `CLST-2020/.github/workflows/codestyle.yaml`.

1. Set up job: sets up a virtual environment to run checks in.
2. Checkout repository
3. Setup Python
4. Install poetry: Update installed packages and install poetry.
5. Restore any cached Poetry dependencies
6. Install any new dependencies: runs `poetry install`.
7. Run black: runs `black` checking for code style errors.
8. Run PyDocStyle: runs pydocstyle checking for missing or wrong documentation within the code.





