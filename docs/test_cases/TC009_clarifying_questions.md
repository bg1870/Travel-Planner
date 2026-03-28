# TC009 — Incomplete Input: Clarifying Questions

**Stages:** Pre-Stage 1 (Information gathering)
**Focus:** The user provides a vague or incomplete request. The orchestrator must ask targeted clarifying questions before proceeding to Stage 1 rather than guessing or making assumptions.

This test case covers three independent sub-scenarios. Each can be run separately.

---

## Sub-scenario A: Missing Dates

**Turn 1 — User:**
> I want to go to Tokyo.

**Expected Response:**

The assistant should ask for missing required details rather than proceeding to planning. Check for all of the following:

- Does not present a travel plan yet
- Asks for at least: departure dates (or travel window), trip duration OR return date, and budget
- May also ask about: origin city (though Cairo is the default origin), travel preferences, number of travelers
- Response is brief and conversational — not an overwhelming list of 10 questions at once
- Tone is helpful and friendly

**Must not include:**
- A Stage 1 travel plan (premature — dates and budget are unknown)
- Assumptions stated as facts (e.g., "I'll assume you're traveling next month")

---

**Turn 2 — User:**
> I want to go in late March for about 10 days. Budget around $2,500.

**Expected Response:**

With the additional details provided, the assistant now has enough to proceed. Check for all of the following:

- Acknowledges the completed details: Cairo → Tokyo, late March, ~10 days, $2,500 budget
- Either proceeds directly to Stage 1 (travel plan) or asks one targeted follow-up (e.g., travel tier preference or number of travelers — if it hasn't been asked)
- Does not ask questions already answered

---

## Sub-scenario B: Missing Budget

**Turn 1 — User:**
> Can you plan a trip to Paris for two weeks in June? Just me.

**Expected Response:**

- Does not present a travel plan yet
- Asks for the budget — this is required for the trip advisor and budget calculator
- May optionally ask about preferences (travel tier, hotel type, flight preferences)
- Does not present generic price ranges as a plan

**Must not include:**
- A Stage 1 travel plan without knowing the budget
- Assuming a budget tier without asking

---

**Turn 2 — User:**
> I'd say around $5,000 is my limit.

**Expected Response:**

- Acknowledges: Cairo → Paris, June, 14 nights, $5,000
- Proceeds to Stage 1 planning (or asks one remaining clarifying question if tier/preferences are genuinely unclear)

---

## Sub-scenario C: Ambiguous Destination

**Turn 1 — User:**
> I want to visit somewhere warm and cheap in Asia for about a week. I have $1,200. I'm from Cairo.

**Expected Response:**

The user has not named a destination. The system supports: Tokyo, Bali, and Istanbul (partial Asia overlap). The assistant should help the user decide rather than silently picking one.

Check for all of the following:

- Does not silently pick a destination and begin planning without user input
- Presents destination options available in the system that match the criteria (warm, cheap, Asia):
  - Bali: very affordable (budget tier $25–$50/day), warm year-round, in Southeast Asia — strong match
  - Tokyo: more expensive (budget tier $60–$80/day), in Asia — may be harder at $1,200 for a week
  - Istanbul: not in Asia (Europe/Middle East) — may or may not be suggested
- Explains why each suggestion fits (or doesn't fit) the criteria
- Asks the user to pick a destination before proceeding

**Must not include:**
- Starting a plan for a destination the user hasn't confirmed
- Presenting destinations outside the mock data as options (the system only has mock data for Paris, Tokyo, New York, Bali, Istanbul)

---

**Turn 2 — User:**
> Let's go with Bali.

**Expected Response:**

- Confirms the destination choice: Cairo → Bali
- Proceeds to Stage 1 (travel plan) using the $1,200 budget and ~7 nights
- Acknowledges that $1,200 is a tight budget for Bali (flights alone can be $520–$880 from mock data) and notes this upfront without blocking the plan
