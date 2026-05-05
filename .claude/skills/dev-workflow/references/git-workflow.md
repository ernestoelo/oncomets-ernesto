# Git Workflow Guide

> **Spanish version available:** [01-git-workflow.es.md](01-git-workflow.es.md).
>
> The English version of this document is the canonical reference.
>
> Last updated: 2026-01-02.

This document defines the mandatory Git workflow conventions for this project.
Its purpose is to ensure consistency, traceability, and maintainability across all repositories,
especially when working with mixed-experience teams and interns. For all the prjects we will use Gitflow.

All contributors must follow these rules.

---

## 0. What is Gitflow?

Gitflow is an alternative Git branching model that involves the use of feature branches and multiple primary branches. 
Compared to trunk-based development, Gitflow has numerous, longer-lived branches and larger commits. Under this model, developers create a feature branch and delay merging it to the main trunk branch until the feature is complete. These long-lived feature branches require more collaboration to merge and have a higher risk of deviating from the trunk branch. They can also introduce conflicting updates.

### How it works
![Gitflow Workflow](../diagrams/imgs/gitflow.png)


### Develop and main branches

Instead of a single `main` branch, this workflow uses two branches to record the history of the project. The `main` branch stores the official release history, and the `develop` branch serves as an integration branch for features. It's also convenient to tag all commits in the `main`branch with a version number.

The first step is to complement the default `main` with a `develop` branch. A simple way to do this is for one developer to create an empty `develop` branch locally and push it to the server:

```
git branch develop
git push -u origin develop
```

This branch will contain the complete history of the project, whereas `main` will contain an abridged version. Other developers should now clone the central repository and create a tracking branch for `develop`.

### Feature branches

#### Create the repository

Each new feature should reside in its own branch, which can be pushed to the central repository for backup/collaboration. But, instead of branching off of `main`, feature branches use `develop` as their parent branch. When a feature is complete, it gets merged back into `develop`. Features should never interact directly with `main`.

![Gitflow Feature Branch](../diagrams/imgs/gitflow-feature-branch.png)

Note that `feature` branches combined with the `develop` branch is, for all intents and purposes, the Feature Branch Workflow. But, the Gitflow workflow doesn’t stop there.

`Feature` branches are generally created off to the latest develop branch.

#### Creating a feature branch

To create a feature branch, first ensure you are on the `develop` branch and have the latest changes:

```sh
git checkout develop
git pull origin develop
```

Then create a new branch for your feature:

```sh
git checkout -b feat/your-feature-name
```

Continue your work and use Git like you normally would.

#### Finishing a feature branch

When you’re done with the development work on the feature, the next step is to merge the `feature_branch` into `develop`. To do this create a pull request from your `feature_branch` to `develop`. After the pull request is reviewed and approved, it can be merged into `develop`.

### Main branch

Once develop has acquired enough features for a release (or a predetermined release date is approaching), you can merge `develop` into `main` to create a new release. This is done via a pull request from `develop` to `main`. After the pull request is reviewed and approved, it can be merged into `main`.

## 1. Branch Naming Convention

All development work must be done in feature branches created from `main`
or an active `release` branch.

### 1.1 Standard Branch Format
All branches must follow this naming convention:

```
type/description-of-change
````

| Prefix | Category | When to Use |
| --- | --- | --- |
| feat | Feature | New functionality (maps to a MINOR release) |
| fix | Bug Fix | Bug or incorrect behavior (PATCH release) |
| refactor | Refactor | Code restructuring without behavior change |
| docs | Documentation | README, guides, API docs |
| style | Style | Formatting only (no logic changes) |
| test | Tests | Adding or fixing tests |
| chore | Maintenance | Tooling, configs, housekeeping |
| hotfix | Critical Fix | Urgent production fix (branch from main) |
| perf | Performance | Performance improvements |
| build | Build System | Dependencies, CI, build tooling |

Examples:

- feat/user-login-bug
- feat/add-shopping-cart-api
- fix/resolve-user-auth-issue
- refactor/update-legacy-styling

### 1.2 Branch Type Prefixes

The same prefixes are used for both branches and commits.
Always keep branch type and commit type consistent.

| Prefix | Category | When to Use |
| --- | --- | --- |
| feat | Feature | New functionality (maps to a MINOR release) |
| fix | Bug Fix | Bug or incorrect behavior (PATCH release) |
| refactor | Refactor | Code restructuring without behavior change |
| docs | Documentation | README, guides, API docs |
| style | Style | Formatting only (no logic changes) |
| test | Tests | Adding or fixing tests |
| chore | Maintenance | Tooling, configs, housekeeping |
| hotfix | Critical Fix | Urgent production fix (branch from main) |
| perf | Performance | Performance improvements |
| build | Build System | Dependencies, CI, build tooling |

Notes on hotfix:

- Use only for critical production issues
- Branch directly from main
- Still requires a Pull Request and review

### 1.3 Best Practices for Branch Descriptions

- Rules:
  - Lowercase only
  - Hyphen-separated
  - Short and descriptive
- Do:
  - feat/enable-dark-mode
  - fix/sidebar-overflow-on-mobile
  - refactor/clean-up-auth-reducer
- Don’t:
  - newbranch
  - fix/bug-i-found
  - Fix_Login_Screen

---

## 2. Commit Message Convention

This project follows the Conventional Commits specification.

### 2.1 Standard Commit Format

```text
type(scope): subject

<body>

<footer>
```

### 2.2 Header (Mandatory)

The header summarizes the change.

- Type (mandatory): Must match the branch prefix (feat, fix, etc.)
- Scope (optional): Affected component (api, ui, auth)
- Subject (mandatory): Short description

Rules:

- Lowercase type and scope
- Imperative, present tense (add, fix, change)
- No period at the end
- Max 50 characters recommended

Examples:

- feat(checkout): add promotional code input
- fix(auth): resolve session cookie issue
- chore(deps): update dependencies

### 2.3 Body (Optional)

- Separated from header by one blank line
- Explain why and how, not what
- Wrap lines at ~72 characters
- Can be omitted if the header is sufficient

### 2.4 Footer (Optional)

Used for:

- Issue references
- Breaking changes

Issue References:

- Closes #123
- Fixes #456
- Refs #789

Breaking Changes:
BREAKING CHANGE: authentication tokens are now short-lived

You may also signal a breaking change with ! in the header:
feat!: change authentication token format

### 2.5 Full Commit Example
```
feat(api): add validation for registration form

This commit adds server-side validation for all fields in the
registration form to prevent malformed data from entering
the database.

It enforces email format checks and password length limits.

Refs #501
Closes #500
```
---

## 3. Expected Daily Workflow

1. Create a branch from main
2. Make small, atomic commits
3. Push changes frequently
4. Open a Pull Request
5. Address review comments
6. Merge only after approval

Direct commits to main are not allowed.

---

## 4. Common Mistakes to Avoid

- Large commits mixing multiple concerns
- Mixing feat and fix in the same commit
- Refactors combined with behavior changes
- Formatting and logic changes together
- Committing secrets or .env files

---

## 5. If You Are Not Sure

If you are unsure about:

- the correct branch type
- commit type or scope
- whether a change is breaking

Ask before committing or opening a PR.
Early questions are always preferred over fixing history later.