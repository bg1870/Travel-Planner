# TC004 — Flight Rejection Only

**Stages:** 1 (Planning) → 2 (Selection) → 2 (Flight retry, hotel preserved)
**Destination:** Cairo → New York
**Budget:** $4,000 total, 7 nights
**Focus:** User approves the hotel but rejects the flight. Only the flight agent re-runs. The previously approved hotel must not change.

---

## Turn 1

**User:**
> I'd like to go from Cairo to New York, September 15–22, total budget $4,000. Mid-range. I prefer direct flights if possible.

**Expected Response — Stage 1: Plan**

- Cairo → New York, September 15–22, 7 nights
- September weather: warm, 25°C, Fashion Week energy, crowds thinning — from mock data
- Budget split shown (~30% flights, ~50% hotels, ~20% activities — New York default)
- Notes that New York is a very high cost-of-living city
- Mentions EgyptAir as a direct route option (MS985, MS987 are direct CAI→JFK flights in mock data)
- Ends with approval question

---

## Turn 2

**User:**
> Approved.

**Expected Response — Stage 2: Selection**

**Flights presented:**
- EgyptAir MS985 ($750, direct, 12h, departs 23:30) — matches direct preference
- EgyptAir MS987 ($820, direct, 12.25h, departs 01:00)
- Turkish Airlines TK1 ($620, 1 stop via IST, 16.5h) — may appear as a budget option
- Emirates EK201 ($880, 1 stop via DXB) — may appear
- Direct flights are highlighted given user preference
- Business class Emirates EK203 ($3,200) must not appear if it would blow the flight budget slice (~$1,200)

**Hotels presented:**
- Up to 3 options within the hotel budget slice (~$2,000 ÷ 7 nights ≈ $285/night ceiling)
- Options from mock data within range: Arlo NoMad ($190/night), The Standard High Line ($290/night), The William Vale ($200/night), Wall Street Hotel ($160/night), Pod 51 ($130/night)
- The Plaza ($550/night × 7 = $3,850) should not be recommended (exceeds hotel slice)

Ends with approval question for both.

---

## Turn 3

**User:**
> The hotel is perfect, I'll take it. But reject the flight — I don't want any layovers, and the direct EgyptAir options depart too late at night for me.

**Expected Response — Flight Retry Only**

The assistant acknowledges the partial approval and re-presents flight options only. Check for all of the following:

- Explicitly confirms the hotel selection is locked in (states the hotel name and price)
- Presents new flight options with constraints applied:
  - No layovers (direct flights only)
  - No late-night departures (the user ruled out 23:30 and 01:00 departures)
- Available direct flights from mock data: MS985 (23:30 — excluded), MS987 (01:00 — excluded)
- **If no direct flights remain within budget at acceptable times:** the assistant must communicate this clearly and suggest options — e.g., accepting a 1-stop flight, adjusting the flight budget, or choosing a different departure day
- Does not re-present any previously rejected flight options

**Must not include:**
- New hotel options or any change to the approved hotel
- Late-night departure options (23:30 or 01:00)
- Non-direct flights presented as "direct"

---

## Constraint Accumulation Check

If a second flight rejection occurs, the next re-run must carry BOTH constraints: "no layovers" AND the original time restriction. Neither constraint is dropped between retries.
