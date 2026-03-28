# Test Cases — Travel Planner QA

Conversation-level test cases for the multi-agent travel planning system. Each test case describes a full or partial conversation with expected assistant behavior per turn.

**Scope:** User-facing message content only — no internal state, tool calls, or agent internals.

**Origin for all test cases:** Cairo (CAI) — the only origin city in the mock data.

---

## Test Case Index

| ID | Title | Stage(s) | Focus |
|----|-------|----------|-------|
| [TC001](TC001_happy_path_paris.md) | Happy Path — Cairo to Paris | 1 → 2 → 3 | Full booking flow, mid-range budget |
| [TC002](TC002_happy_path_bali.md) | Happy Path — Cairo to Bali | 1 → 2 → 3 | Full booking flow, budget travel |
| [TC003](TC003_plan_rejection.md) | Plan Rejection — Budget Reallocation | 1 (retry) | User rejects plan, constraint added, plan revised |
| [TC004](TC004_flight_rejection.md) | Flight Rejection Only | 2 (flight retry) | User approves hotel, rejects flight; only flight re-runs |
| [TC005](TC005_hotel_rejection.md) | Hotel Rejection Only | 2 (hotel retry) | User approves flight, rejects hotel; only hotel re-runs |
| [TC006](TC006_both_rejected.md) | Both Flight and Hotel Rejected | 2 (full retry) | User rejects both; both re-run with accumulated constraints |
| [TC007](TC007_triple_rejection_escalation.md) | Triple Rejection Escalation | 2 (escalation) | Same stage rejected 3 times; orchestrator suggests upstream changes |
| [TC008](TC008_booking_cancellation.md) | Booking Cancellation | 3 | User cancels at final confirmation; returns to selection review |
| [TC009](TC009_clarifying_questions.md) | Incomplete Input — Clarifying Questions | Pre-Stage 1 | User gives vague request; orchestrator asks for missing details |

---

## How to Use These Test Cases

1. Run the system with mock data active (all routes originate from Cairo).
2. Enter each user message exactly as shown, in order.
3. Check the assistant response against the **Expected Response** criteria — key phrases and structural elements to verify are listed as bullet points.
4. **Pass:** All listed criteria are satisfied.
5. **Fail:** Any listed "must include" item is absent, or any "must not include" item is present.

Response criteria use approximate matching — exact wording will vary per run.
