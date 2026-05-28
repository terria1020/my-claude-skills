---
name: experiment-builder
description: Convert uncertain technical ideas into small runnable experiments. Use when the user asks for a PoC, spike, sample project, first project structure, test harness, throwaway script, mock server, fixture, seed data, Helm chart, docker-compose setup, Makefile, sample app, temporary validation tool, or when an architecture change, new integration, external system, data pipeline, messaging/cache/observability/deployment/API/data-modeling decision would benefit from a small executable experiment before full implementation.
---

# Experiment Builder

## Core Rule

Reduce uncertainty with the smallest runnable experiment that can answer a design question. Do not turn an uncertain idea into a production-scale implementation unless the user explicitly asks for that.

## Response Workflow

1. Split the idea into assumptions and experiments:
   - Restate the idea briefly.
   - Extract the key assumptions to validate.
   - Map each assumption to a possible experiment.

2. Decide whether an experiment is useful:
   - If a small code/config change in the existing repo is enough, prefer that over a new project.
   - If design review is more useful than implementation, say so and avoid pushing code.
   - If runtime behavior would materially improve the decision, propose a small PoC.

3. Offer 1-3 experiment options when the next step is not obvious:
   - For each option, state purpose, scope, artifacts, rough effort, and what it teaches.
   - Include success criteria, failure criteria, observed signals, and discard criteria.
   - Prefer "local first" experiments unless the question is specifically about deployment or operations.

4. Build when requested or clearly implied:
   - If the user says "make it", "set it up", "run it", "PoC 만들어줘", "돌려보자", or similar, proceed without asking for permission.
   - Create the smallest valid structure: docker-compose, Helm chart, Makefile, sample app, mock server, fixture, seed data, test harness, CLI script, sample config, or project skeleton as appropriate.
   - Follow the existing repository structure and conventions first.
   - Avoid large frameworks, deployment pipelines, or monorepo structures unless they are required to answer the experiment question.

5. Keep artifacts disposable but trustworthy:
   - Do not over-abstract throwaway code.
   - Keep enough structure that someone can run, inspect, and delete it.
   - Include execution commands, example input, expected or observable output, validation steps, and teardown/cleanup steps.
   - Separate PoC assumptions from production requirements when security, cost, reliability, or operations matter.

6. Validate the experiment:
   - Run the smallest meaningful command that proves the artifact works.
   - Capture errors and tighten the experiment until it either runs or has a clear blocker.
   - Report what was verified, what failed, and what remains uncertain.

7. Connect results to the design decision:
   - Explain what the experiment proves or disproves.
   - State the next decision point.
   - Recommend whether to continue, change direction, gather more evidence, or discard the PoC.

## Design Principles

- Prefer evidence over impressive demos.
- Keep the experiment narrow and tied to at least one design question.
- Make success and failure cheap to observe.
- Avoid production polish unless it affects the validity of the result.
- Use mock dependencies when they answer the question; use real dependencies when integration behavior is the question.
- Do not hide important operational gaps behind a local-only success.

## Tone

- Be practical and fast-moving.
- Lower uncertainty into an executable next step.
- Use conditional confidence: "this proves X under these limits."
- Use natural Korean when responding in Korean.

## Avoid

- Do not present the skill as production implementation.
- Do not create a new project when a small existing-repo addition is enough.
- Do not force implementation when the user only asked for design review.
- Do not leave generated artifacts without run, observe, and cleanup instructions.
