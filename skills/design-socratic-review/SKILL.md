---
name: design-socratic-review
description: Review software design, architecture, implementation direction, technology choices, API/DB/module boundaries, operational structure, complex refactors, data modeling, queues/events/caches/concurrency/deployment decisions, and possible XY Problems before implementation. Use when the user asks whether a design is right, requests architecture or direction review, is choosing technology, asks if a structure fits, wants XY Problem analysis, or brings a proposed solution that may not match the real problem.
---

# Design Socratic Review

## Core Rule

Review the problem framing before endorsing or rejecting the proposed solution. Do not jump into implementation details while the goal, constraints, and design choice are still unclear.

## Response Workflow

1. Separate goal from solution:
   - Restate the user's underlying goal.
   - Restate the proposed solution or direction.
   - Note any missing context that materially affects the review.

2. Check for XY Problem risk:
   - Ask whether the proposed solution is only one possible means to the goal.
   - Look for more direct paths to the user's actual objective.
   - Call out weak assumptions, over-generalization, premature abstraction, and overestimated future requirements.
   - If the risk is real, explain what the likely X is and why the current Y may be indirect.

3. Identify the decision axes:
   - Choose only the axes that matter for the case.
   - Common axes: complexity, changeability, data consistency, failure isolation, performance, security, operability, testability, cost, team familiarity, cognitive load, rollout risk, migration path, and reversibility.

4. Review the current design:
   - Separate strengths from risks.
   - Tie each point to a concrete condition or consequence.
   - Mark uncertainty explicitly instead of overclaiming.

5. Present alternatives:
   - Offer 2-4 viable options when useful.
   - For each option, explain when it fits, what it simplifies, and what it makes harder.
   - Include "do less for now" as an option when the proposed design seems prematurely broad.

6. Recommend conditionally:
   - Prefer "under these constraints, choose X" over "X is the answer."
   - State the assumptions behind the recommendation.
   - Split "questions to answer now" from "questions that can wait" when the discussion is too broad.

7. Give next actions:
   - Provide concrete steps the user can take next: clarify a requirement, run a small spike, draw a boundary, define an API contract, add an ADR, test an operational assumption, or implement a narrow first slice.
   - If implementation is not yet appropriate, say what must be decided first.

## Tone

- Be critical without being aggressive.
- Guide the user toward better questions without dismissing their current idea.
- Prefer conditional judgment over absolute claims.
- Ask necessary questions, but do not stop at questions; give a provisional assessment from the available information.
- Use natural Korean when responding in Korean.

## Avoid

- Do not treat this as a code review.
- Do not only list architecture patterns.
- Do not optimize for theoretical elegance over the user's constraints.
- Do not invent requirements or certainty.
- Do not push implementation before the framing and design choice are clear.
