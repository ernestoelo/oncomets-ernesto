# Dev workflow

> **Spanish version available:** [README.es.md](README.es.md).
>
> The English version of this document is the canonical reference.
>
> Last updated: 2026-01-02.

This repository defines the development workflows, technical standards
and operational guidelines used across the organization.

The objective of these documents is to ensure:

- Predictable system behavior
- Reproducible environments
- Clear ownership and responsibility
- Fast onboarding of new team members and interns

These guidelines apply to:

- Web systems
- Mobile applications
- Backend services
- Infrastructure-related repositories
- Internal tools and operational software

Unless explicitly stated otherwise, all new projects must follow
the standards defined in this repository.

## Repository Structure

This repository is organized by domain.

- [guides/01-git-workflow.md](guides/01-git-workflow.md): Defines branching, commit conventions and repository usage.
- [guides/01-git-workflow.es.md](guides/01-git-workflow.es.md): Spanish version of the Git workflow guide.
- [guides/02-ai-development.md](guides/02-ai-development.md): Mandatory structure and operational requirements for AI/ML projects.
- [guides/02-ai-development.es.md](guides/02-ai-development.es.md): Spanish version of the AI development guide.
- [checklists/02-ai-development.checklist.md](checklists/02-ai-development.checklist.md): Self-validation checklist for AI/ML projects.
- [guides/03-web-and-mobile-systems.md](guides/03-web-and-mobile-systems.md): Mandatory structure and operational requirements for Web, Mobile and Software Systems.
- [guides/03-web-and-mobile-systems.es.md](guides/03-web-and-mobile-systems.es.md): Spanish version of the Web and Mobile Systems guide.

- [checklists/03-web-and-mobile-systems.checklist.md](checklists/03-web-and-mobile-systems.checklist.md): Self-validation checklist for Web and Mobile systems.

- [templates/README.template.md](templates/README.template.md): Official README template for project repositories.
- [templates/03-web-and-mobile-systems.diagram-template.md](templates/03-web-and-mobile-systems.diagram-template.md): Minimal production architecture diagram template.

- [diagrams/templates/](diagrams/templates/): Diagram image templates (overview, architecture, production).
- [diagrams/examples/](diagrams/examples/): Real-world diagram examples from production systems.

## How to Use These Guides

These documents are not reference material only.

They are intended to be used as:

- Starting point for new repositories
- Baseline for system design
- Operational contract between team members
- Self-validation tool before deployment or handover

## Mandatory Artifacts per Repository

Every project repository must include:

- A README.md following the official template
- At least one production architecture diagram
- Scripted setup and deployment
- Clear separation between development and production

## Responsibility and Ownership

Each project team is fully responsible for:

- Following the applicable guidelines
- Keeping documentation aligned with reality
- Ensuring scripts are functional and reproducible
- Verifying their system before production use

There is no external review requirement.
Ownership is explicit and local to the team.

## Guiding Principles

- Clarity over cleverness
- Reproducibility over convenience
- Explicit behavior over assumptions
- Undocumented behavior is considered non-existent

## Evolution of the Standards

These guidelines are living documents.

Changes should be:

- Motivated by real operational needs
- Backward-compatible when possible
- Clearly documented
